import os
import time

from langchain.tools import DuckDuckGoSearchRun
from langchain.agents.tools import Tool
from langchain import OpenAI
from langchain.agents import initialize_agent
from langchain.chains import LLMMathChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st


from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

OpenAI_key = os.environ.get("OPENAI_API_KEY")

st.title("Conversational Agent")

# Initialize the session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the conversation memory
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history")

# Initialize the language model and tools
llm = OpenAI(temperature=0)
search = DuckDuckGoSearchRun()
llm_math_chain = LLMMathChain(llm=llm, verbose=True)

tools = [
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="Useful for answering math questions.",
    ),
    Tool(
        name="DuckDuckGo Search",
        func=search.run,
        description="Useful for internet searches when information isn't readily available.",
    )
]

# Initialize the conversational agent
conversational_agent = initialize_agent(
    agent="conversational-react-description",
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=10,
    memory=st.session_state.memory
)

# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture the user's input
question = st.chat_input("Ask me any question")

if question:
    # Add the user's question to the chat container
    with st.chat_message("user"):
        st.markdown(question)

    # Save the user's message to the session state
    st.session_state.messages.append({"role": "user", "content": question})

    # Generate the assistant's response
    with st.chat_message("assistant"):
        # Set up the Streamlit callback handler
        st_callback = StreamlitCallbackHandler(st.container())
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = conversational_agent.run(question, callbacks=[st_callback])

        # Simulate a streaming response with a slight delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")

        # Display the final response
        message_placeholder.info(full_response)

    # Save the assistant's response to the session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
