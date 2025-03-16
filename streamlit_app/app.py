import os
from pathlib import Path
import base64

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

import streamlit as st


from dotenv import load_dotenv, find_dotenv

from tools import local_codebox_tool, LocalCodeBoxToolRunManager
from streamlit_callback import CustomStreamlitCallbackHandler

# Load environment variables but we'll prioritize user-provided keys
load_dotenv(find_dotenv())

DATALAB_API_PROMPT: str = (
    Path(__file__).parent.parent / "prompts" / "datalab-api-prompt.md"
).read_text()
MODEL_OPTIONS = {
    "Claude 3 Haiku": "claude-3-5-haiku-latest",
    "Claude 3.7 Sonnet": "claude-3-7-sonnet-latest",
    "GPT-4o": "gpt-4o",
    "OpenAI o3-mini": "o3-mini",
    "GPT-3.5 Turbo": "gpt-3.5-turbo",
}
DEFAULT_MODEL = "claude-3-haiku-20240307"

DEFAULT_DATALAB_API_URL = "https://demo.datalab-org.io"

SYSTEM_PROMPT = f"""You are a virtual data management assistant that helps materials chemists
manage their experimental data and plan experiments. 
You can use a code interpreter tool to assist you (only if needed). If you use the code interpreter, 
DO NOT EXPLAIN THE CODE. Instead, just use the output of the code
to answer the question the user asked. 
Here is some more info about the datalab API: {DATALAB_API_PROMPT}"""


codebox = LocalCodeBoxToolRunManager.instance().codebox


def initialize_api_keys():
    """Initialize API keys from session state or environment variables"""
    # Set up session state for API keys if not already present
    if "api_keys_submitted" not in st.session_state:
        st.session_state.api_keys_submitted = False

    if "anthropic_api_key" not in st.session_state:
        st.session_state.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = os.environ.get("OPENAI_API_KEY", "")

    if "datalab_api_key" not in st.session_state:
        st.session_state.datalab_api_key = os.environ.get("DATALAB_API_KEY", "")

    if "datalab_api_url" not in st.session_state:
        st.session_state.datalab_api_url = DEFAULT_DATALAB_API_URL

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = DEFAULT_MODEL


def get_llm():
    """Get the LLM based on the selected model and API keys"""
    model_name = st.session_state.selected_model

    if model_name.startswith("claude"):
        if not st.session_state.anthropic_api_key:
            return None
        return ChatAnthropic(
            anthropic_api_key=st.session_state.anthropic_api_key,
            model=model_name,
        )
    elif model_name.startswith("gpt") or model_name.startswith("o3"):
        if not st.session_state.openai_api_key:
            return None
        return ChatOpenAI(
            api_key=st.session_state.openai_api_key,
            model=model_name,
        )
    return None


messages_template = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# st.set_page_config(layout="wide")
st.title("Materials Data Analysis Agent")

st.markdown("""
### Welcome to the Materials Data Analysis Assistant

This tool helps materials chemists manage experimental data and plan experiments. You can:

- **Upload data files** for analysis
- **Ask questions** about your materials data
- **Get help planning** new experiments
- **Visualize results** using the built-in code interpreter

The assistant uses AI to understand your needs and can execute Python code to analyze your data.
Simply upload your files and ask questions in natural language.
""")

# Initialize API keys
initialize_api_keys()

# Create sidebar for API key inputs
with st.sidebar:
    st.header("API Keys")

    with st.form("api_keys_form"):
        st.selectbox(
            "Select LLM Model",
            options=list(MODEL_OPTIONS.keys()),
            index=list(MODEL_OPTIONS.values()).index(st.session_state.selected_model)
            if st.session_state.selected_model in MODEL_OPTIONS.values()
            else 0,
            key="model_selection",
        )

        st.text_input(
            "Anthropic API Key (for Claude models)",
            value=st.session_state.anthropic_api_key,
            type="password",
            key="anthropic_key_input",
        )

        st.text_input(
            "OpenAI API Key (for GPT models)",
            value=st.session_state.openai_api_key,
            type="password",
            key="openai_key_input",
        )

        st.text_input(
            "Datalab API URL",
            value=st.session_state.datalab_api_url,
            key="datalab_api_url_input",
        )

        st.text_input(
            "Datalab API Key",
            value=st.session_state.datalab_api_key,
            type="password",
            key="datalab_key_input",
        )

        submit_button = st.form_submit_button("Save API Keys")

        if submit_button:
            st.session_state.anthropic_api_key = st.session_state.anthropic_key_input
            st.session_state.openai_api_key = st.session_state.openai_key_input
            st.session_state.datalab_api_key = st.session_state.datalab_key_input
            st.session_state.datalab_api_url = st.session_state.datalab_api_url_input
            st.session_state.selected_model = MODEL_OPTIONS[
                st.session_state.model_selection
            ]
            st.session_state.api_keys_submitted = True
            st.success("API keys saved!")

# Initialize the session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT.replace("{{ DATALAB_API_URL }}", st.session_state.datalab_api_url)}]

if "files" not in st.session_state:
    st.session_state.files = codebox.list_files()

# Display files in sidebar
with st.sidebar:
    st.header("Files")
    if st.session_state.files:
        for file in st.session_state.files:
            with open(os.path.join(".codebox", file.name), "rb") as f:
                btn = st.download_button(
                    label=file.name,
                    data=f.read(),
                    file_name=file.name,
                    mime="image/png",
                )

# Check if required API keys are provided
llm = get_llm()
if not llm:
    st.warning(
        "Please provide the appropriate API key for your selected model in the sidebar."
    )
    st.stop()

tools = [local_codebox_tool]

# bind tools
llm_with_tools = llm.bind_tools(tools)

# Initialize the conversational agent
agent = create_tool_calling_agent(llm_with_tools, tools, messages_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "system":
            with st.expander("Show system prompt", expanded=False):
                st.write(message["content"])
        else:
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
        file_bytes = uploaded_file.getvalue()
        with open(os.path.join(".codebox", uploaded_file.name), "wb") as f:
            f.write(file_bytes)

        st.session_state.files = codebox.list_files()

        encoded_string = base64.b64encode(file_bytes).decode("utf-8")
        # st.write(bytes_data)

        if uploaded_file.type in ("image/jpeg", "image/png"):
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": question,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{uploaded_file.type};base64,{encoded_string}"
                        },
                    },
                ]
            )

        else:
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": f"A file named {uploaded_file.name} was uploaded and can be accessed using code. {question}",
                    }
                ]
            )

    else:
        message = HumanMessage(content=[{"type": "text", "text": question}])

    # Add the user's question to the chat container
    with st.chat_message("user"):
        st.markdown(question)

    # Save the user's message to the session state
    st.session_state.messages.append({"role": "user", "content": message.content})

    # Set up the Streamlit callback handler
    st_callback = CustomStreamlitCallbackHandler(
        st.container(), max_thought_containers=20, expand_new_thoughts=True
    )

    response = agent_executor.invoke(
        {"chat_history": st.session_state.messages}, {"callbacks": [st_callback]}
    )

    with st.chat_message("assistant"):
        st.markdown(response["output"])

    # Save the assistant's response to the session state
    st.session_state.messages.append(
        {"role": "assistant", "content": response["output"]}
    )
