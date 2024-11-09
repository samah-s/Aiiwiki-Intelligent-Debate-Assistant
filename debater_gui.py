import streamlit as st
import re
import base64
from debater_program import IntelligentDebater  # assuming both files are in the same directory

# Streamlit App Configurations
st.set_page_config(page_title="Aiiwiki", layout="wide")
st.title("Aiiwiki - Intelligent Debate Assistant 🧠")

# Sidebar - Title, description, and topic input
with st.sidebar:
    st.markdown("""
    Aiiwiki will respond with intelligent rebuttals to your arguments.
    Enter a topic to help Aiiwiki prepare for the debate, and challenge it with arguments!
    
    Created by: [Samah Syed](https://github.com/samah-s)
    """, unsafe_allow_html=True)
    
    # Step 1: Enter a debate topic
    topic = st.text_input("Enter the debate topic:")

if topic:
    debater = IntelligentDebater(topic)
    
    # Fetch Wikipedia content
    wiki_content = debater.fetch_wiki_content(topic)
    
    if wiki_content:
        # Add direct download option in the sidebar using Streamlit's download_button
        with st.sidebar:
            st.success("Knowledge base generated successfully!")
            
            # Create the download button
            st.download_button(
                label="Download the source",
                data=wiki_content,
                file_name=f"{topic}_wiki_content.html",
                mime="text/html",
            )

        # Initialize the knowledge base with topic content
        debater.build_knowledge_base()

        # Create a session state to store conversation history
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "Hello, I'm Aiiwiki! I'm ready to rebut on the topic - "+ topic}]
        
        # Display previous messages (conversation history)
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        # Step 2: Chat input (debate arguments and rebuttals)
        user_argument = st.chat_input("Enter your argument here:")
        
        if user_argument:
            # Add user input to the conversation history
            st.session_state.messages.append({"role": "user", "content": user_argument})
            st.chat_message("user").write(user_argument)
            
            # Update the knowledge base with the user input
            debater.build_knowledge_base(user_argument)
            
            # Get a rebuttal from the debater
            rebuttal = debater.find_rebuttal(user_argument)
            rebuttal = re.sub(r'\[[^\]]*\]', '', rebuttal)
            
            # Add the rebuttal to the conversation history
            st.session_state.messages.append({"role": "assistant", "content": rebuttal})
            st.chat_message("assistant").write(rebuttal)
