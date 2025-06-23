import streamlit as st

st.header("Word Frequency Counter")

user_input = st.chat_input("Type your message here...")

if user_input:
  
    word_count = {}
    for word in user_input.split():
        word = word.lower().strip(".,!?")  
        word_count[word] = word_count.get(word, 0) + 1
    
    st.subheader("Word Count Result:")
    st.write(word_count)
else:
    st.info("Please enter some text above to get word frequencies.")
