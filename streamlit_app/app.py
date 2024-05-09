import os
from pathlib import Path
import base64

from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.agents.tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.messages import HumanMessage

from langchain.agents import initialize_agent
from langchain.chains import LLMMathChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st
from st_multimodal_chatinput import multimodal_chatinput


from dotenv import load_dotenv, find_dotenv

from tools import local_codebox_tool, LocalCodeBoxToolRunManager
from streamlit_callback import CustomStreamlitCallbackHandler

load_dotenv(find_dotenv())

DATALAB_API_PROMPT: str = (Path(__file__).parent.parent / "prompts" / "datalab-api-prompt.md").read_text()
MODEL_NAME = "claude-3-haiku-20240307"
SYSTEM_PROMPT = f"""You are a virtual data managment assistant that helps materials chemists
manage their experimental data and plan experiments. 
You can use a code interpreter tool to assist you (only if needed). If you use the code interpreter, 
DO NOT EXPLAIN THE CODE. Instead, just use the output of the code
to answer the question the user asked. 
Here is some more info about the datalab API: {DATALAB_API_PROMPT}"""


codebox = LocalCodeBoxToolRunManager.instance().codebox

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

# st.set_page_config(layout="wide")
st.title("Conversational Agent")

# Initialize the session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "files" not in st.session_state:
    st.session_state.files = codebox.list_files()

if st.session_state.files:
    st.sidebar.write("Uploaded Files:")
    for file in st.session_state.files:
        with open(os.path.join(".codebox", file.name), "rb") as f:
            btn = st.sidebar.download_button(label=file.name, data=f.read(), file_name=file.name, mime="image/png")

tools = [local_codebox_tool]

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
uploaded_file = st.file_uploader("Choose a file")


#     content: [
#         {
#             "type": "image_url",
#     image_url: "data:image/jpeg;base64,{base64Image}",
#   },
# ],

if question:
    if uploaded_file is not None:
        encoded_string = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        # st.write(bytes_data)
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": question,
                },
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}},
            ]
        )
        print("CREATED A NEW MESSAGE:")
        print(message.content)
    else:
        message = HumanMessage(content=[{"type": "text", "text": question}])
    # base64ImageMessage = HumanMessage(
    #     content=[
    #         {
    #             "type": "image_url",
    #             "image_url": "https://avatars.githubusercontent.com/u/126733545?s=200&v=4",
    #         }
    #     ]
    # )

    # print(base64ImageMessage)

    # Add the user's question to the chat container
    with st.chat_message("user"):
        st.markdown(question)

    # Save the user's message to the session state
    st.session_state.messages.append({"role": "user", "content": message.content})

    # Set up the Streamlit callback handler
    st_callback = CustomStreamlitCallbackHandler(st.container(), max_thought_containers=20, expand_new_thoughts=True)

    response = agent_executor.invoke({"chat_history": st.session_state.messages}, {"callbacks": [st_callback]})

    with st.chat_message("assistant"):
        st.markdown(response["output"])

    # Save the assistant's response to the session state
    st.session_state.messages.append({"role": "assistant", "content": response["output"]})
