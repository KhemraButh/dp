import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')
    
    # Check for API token in secrets or input
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
        st.success('API key loaded from secrets!', icon='✅')
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if replicate_api:
            if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
                st.warning('Please enter a valid Replicate API token!', icon='⚠️')
                st.info('Token should start with "r8_" and be 40 characters long')
            else:
                st.success('API token looks valid!', icon='👉')
        else:
            st.warning('Please enter your Replicate API token to continue.', icon='⚠️')
    
    # Set environment variable if token is provided
    if replicate_api and replicate_api.startswith('r8_') and len(replicate_api)==40:
        os.environ['REPLICATE_API_TOKEN'] = replicate_api
    else:
        # Clear the token if it's invalid
        if 'REPLICATE_API_TOKEN' in os.environ:
            del os.environ['REPLICATE_API_TOKEN']

    st.subheader('Models and parameters')
    
    # Updated model references (current as of 2024)
    selected_model = st.selectbox('Choose a Llama2 model', 
                                 ['Llama2-7B', 'Llama2-13B', 'Llama2-70B'], 
                                 key='selected_model')
    
    # Current model versions (check https://replicate.com for latest)
    model_versions = {
        'Llama2-7B': 'meta/llama-2-7b-chat:13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0',
        'Llama2-13B': 'meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d',
        'Llama2-70B': 'meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3'
    }
    
    llm = model_versions.get(selected_model, model_versions['Llama2-7B'])
    
    temperature = st.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01,
                           help='Controls randomness: Lower = more deterministic, Higher = more creative')
    top_p = st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01,
                     help='Controls diversity via nucleus sampling: 0.5 means half of all likelihood-weighted options are considered')
    max_length = st.slider('max_length', min_value=64, max_value=4096, value=512, step=64,
                          help='Maximum length of the generated response')
    
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history, 
                 help="Clear the current conversation")

# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input):
    # Check if API token is set
    if 'REPLICATE_API_TOKEN' not in os.environ:
        return "Error: Replicate API token not set. Please check your API token in the sidebar."
    
    try:
        # Build the conversation history
        string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
        for dict_message in st.session_state.messages:
            if dict_message["role"] == "user":
                string_dialogue += "User: " + dict_message["content"] + "\n\n"
            else:
                string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
        
        # Generate response using Replicate
        output = replicate.run(
            llm,
            input={
                "prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                "temperature": temperature, 
                "top_p": top_p, 
                "max_length": max_length, 
                "repetition_penalty": 1.1  # Slightly increased to reduce repetition
            }
        )
        
        # Collect the output
        full_response = ""
        for item in output:
            full_response += item
        
        return full_response
        
    except replicate.exceptions.ReplicateError as e:
        return f"Replicate API Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    # Check if we have a valid API token
    if not replicate_api or not (replicate_api.startswith('r8_') and len(replicate_api)==40):
        with st.chat_message("assistant"):
            st.error("Please enter a valid Replicate API token in the sidebar to use the chatbot.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt)
                placeholder = st.empty()
                
                if response.startswith("Error:"):
                    st.error(response)
                else:
                    placeholder.markdown(response)
                    
                    # Add to message history
                    message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(message)

# Add some helpful information
with st.expander("Troubleshooting Tips"):
    st.markdown("""
    **Common Issues and Solutions:**
    
    1. **Invalid API Token**: 
       - Make sure your token starts with `r8_` and is 40 characters long
       - Get your token from [Replicate](https://replicate.com/account/api-tokens)
       
    2. **Billing Issues**:
       - Check your Replicate account has available credits
       - Add a payment method if needed
       
    3. **Model Access**:
       - Some models require explicit access approval
       - Check the model page on Replicate for access requirements
       
    4. **Rate Limits**:
       - You might be hitting API rate limits
       - Free tier has limitations on usage
    """)

# Footer
st.markdown("---")
st.caption("Note: This chatbot uses Llama 2 models via Replicate API. You need a valid API token to use it.")
