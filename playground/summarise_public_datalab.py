"""WARNING: this costs (someone) money

You will need to an ANTHROPIC_API_KEY and a DATALAB_API_KEY.

"""

from codeinterpreterapi import CodeInterpreterSession, settings
from pathlib import Path

settings.MODEL = "claude-3-haiku-20240307"
settings.CUSTOM_PACKAGES = ["datalab-api"]

SYSTEM_PROMPT = (
    Path(__file__).parent.parent / "prompts" / "datalab-api-prompt.md"
).read_text()

while True:
    with CodeInterpreterSession(
        verbose=True,
    ) as session:
        # generate a response based on user input
        task = input("$: ")
        response = session.generate_response(SYSTEM_PROMPT.replace("$(TASK)", task))
        # output the response
        response.show()
