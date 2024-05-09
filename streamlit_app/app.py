import os
from pathlib import Path

from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.agents.tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from langchain.agents import initialize_agent
from langchain.chains import LLMMathChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st


from dotenv import load_dotenv, find_dotenv

from tools import local_codebox_tool

load_dotenv(find_dotenv())

DATALAB_API_PROMPT: str = (Path(__file__).parent.parent / "prompts" / "datalab-api-prompt.md").read_text()
MODEL_NAME = "claude-3-haiku-20240307"
SYSTEM_PROMPT = f"""You are a virtual data managment assistant that helps materials chemists
manage their experimental data and plan experiments. 
You can use a code interpreter tool to assist you (only if needed).
Here is some more info about the datalab API: {DATALAB_API_PROMPT}"""



if MODEL_NAME.startswith("claude"):
    llm = ChatAnthropic(
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        model=MODEL_NAME,
    )
elif MODEL_NAME.startswith("gpt"):
    llm = ChatOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model=MODEL_NAME,
    )

messages_template = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

st.title("Conversational Agent")

# Initialize the session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# # Initialize the conversation memory
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]


search = DuckDuckGoSearchRun()
# llm_math_chain = LLMMathChain(llm=llm, verbose=True)

tools = [
    local_codebox_tool,
    # Tool(
    #     name="Calculator",
    #     func=llm_math_chain.run,
    #     description="Useful for answering math questions.",
    # ),
    # Tool(
    #     name="DuckDuckGo Search",
    #     func=search.run,
    #     description="Useful for internet searches when information isn't readily available.",
    # ),
    # codeboxtool,
]

# bind tools
llm_with_tools = llm.bind_tools(tools)

# Initialize the conversational agent
agent = create_tool_calling_agent(llm_with_tools, tools, messages_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture the user's input
question = st.chat_input("Give me a task or ask me any question")

if question:
    # Add the user's question to the chat container
    with st.chat_message("user"):
        st.markdown(question)

    # Save the user's message to the session state
    st.session_state.messages.append({"role": "user", "content": question})

    # Set up the Streamlit callback handler
    st_callback = StreamlitCallbackHandler(
        st.container(), max_thought_containers=20, expand_new_thoughts=True
    )

    response = agent_executor.invoke(
        {"chat_history": st.session_state.messages}, {"callbacks": [st_callback]}
    )

    with st.chat_message("assistant"):
        st.markdown(response["output"])

    breakpoint()

    # # Generate the assistant's response
    # with st.chat_message("assistant"):
    #     # Set up the Streamlit callback handler
    #     st_callback = StreamlitCallbackHandler(st.container())
    #     # message_placeholder = st.empty()
    #     full_response = ""

    #     response = agent_executor.invoke({"chat_history": st.session_state.chat_history}, callbacks=[st_callback])
    #     # breakpoint()

    #     # # Simulate a streaming response with a slight delay
    #     # for chunk in response["output"].split():
    #     #     full_response += chunk + " "
    #     #     time.sleep(0.05)
    #     #     message_placeholder.markdown(full_response + "▌")

    #     # Display the final response
    #     message_placeholder.markdown(response["content"])

    # Save the assistant's response to the session state
    st.session_state.messages.append(
        {"role": "assistant", "content": response["output"]}
    )
