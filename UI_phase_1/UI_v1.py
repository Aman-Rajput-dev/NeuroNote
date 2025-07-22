import streamlit as st
import random
import time
from datetime import datetime
import streamlit as st

# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

def get_greeting():
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good morning!"
    elif 12 <= current_hour < 17:
        return "Good afternoon!"
    elif 17 <= current_hour < 21:
        return "Good evening!"
    else:
        return "Good night!"

gradient_text_html = """
    <style>
    .gradient-text{
        background: linear-gradient(74deg,#4285f4 0,#9b72cb 9%,#d96570 20%,#d96570 24%,#9b72cb 35%,#4285f4 44%,#9b72cb 50%,#d96570 56%,#131314 75%,#131314 100%);
        -webkit-background-clip: text;
        color: transparent;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom:0px;
        
    }
    </style>

    <div class="gradient-text">
    NeuroNote
    </div>
    """



def main():

    st.set_page_config(page_title="NeuroNote",
                        page_icon=":books:",
                        layout="wide"
    )


    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []


    # Display greeting only if user hasn't entered input
    if not st.session_state.messages:
        st.markdown(gradient_text_html, unsafe_allow_html=True)
        st.title(get_greeting())
        st.header("How can I help you today with your studies?")
        st.markdown("""
            <style>
            .st-emotion-cache-zy6yx3 {
                padding-top: 5rem;
                padding-bottom: 5rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
            </style>
            """, unsafe_allow_html=True)
    
    

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator())
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()