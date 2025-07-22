import streamlit as st
import random
import time
from datetime import datetime
import streamlit as st
import os
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

def image_generator():
    img_response = random.choice([r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.1.jpg"])
    return img_response

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
    
    # with st.sidebar:
    #     with st.echo():
    #         st.write("This code will be printed to the sidebar.")

    #     with st.spinner("Loading..."):
    #         time.sleep(5)
    #     st.success("Done!")

    col1, col2 = st.columns(2)

    with col1:
        messages = st.container()
        # Accept user input
        if prompt := st.chat_input("What is up?"):
            messages.chat_message("user").write(prompt)
            response = response_generator()
            messages.chat_message("assistant").write_stream(response_generator())
    with col2:
        img_list = [r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.1.jpg",r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.2.jpg",r"C:\Users\student\Desktop\202418003\Minor Project\Class 12\UI\Class_12_Figure 1.3.jpg"]
        
        cols = st.columns(len(img_list)) # Creates one column per image

        # Display images horizontally
        for col, img_url in zip(cols, img_list):
            with col:
                st.image(img_url, caption= os.path.basename(img_url))
        
            

if __name__ == "__main__":
    main()