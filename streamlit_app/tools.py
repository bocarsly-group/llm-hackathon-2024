from uuid import uuid4
from io import BytesIO
import re
import base64

from pydantic.v1 import BaseModel, Field
from langchain_core.tools import tool, StructuredTool

from codeboxapi import CodeBox, settings
from codeboxapi.box.localbox import LocalBox
from codeboxapi.schema import CodeBoxOutput

from codeinterpreterapi import File
# from codeinterpreterapi.chains import get_file_modifications


# Allow the LLM to see more of the Python output
settings.MAX_OUTPUT_LENGTH = 1000

TOOL_DESCRIPTION = """Input a string of code to a ipython interpreter.
Write the entire code in a single string.
This string can be really long, so you can use the `;` character to split lines.
Start your code on the same line as the opening quote.
Do not start your code with a line break.
For example, do 'import numpy', not '\\nimport numpy'.

Variables are preserved between runs.

You can use all Python 3.10 standard library, plus also: numpy, pandas, matplotlib, seaborn, scikit-learn and scipy.

You should return _ALL_ of the Python output as a nicely formatted string in your response.
"""


@tool
def codeboxtool(code: str) -> str:
    """A custom tool for executing Python code in a local
    [Codebox](https://github.com/shroominic/codebox-api).

    Input a string of code to an ipython interpeter, and get the result back.
    Remember to always use double quotes only when generating json.
    The start of the result will be list of files generated, then any printed text will be shown.

    """

    with CodeBox() as codebox:
        output = codebox.run(code)
        output_files = codebox.list_files()

    output_content = output.content

    if output.type == "image/png":
        filename = f"image-{uuid4()}.png"
        # file_buffer = BytesIO(base64.b64decode(output.content))
        # file_buffer.name = filename
        output_files.append(filename)
        output_content = ""

    elif output.type == "error":
        print("Error:", output.content)
        if "ModuleNotFoundError" in output.content:
            if package := re.search(
                r"ModuleNotFoundError: No module named '(.*)'",
                output.content,
            ):
                codebox.install(package.group(1))
                return f"{package.group(1)} was missing but it has now been installed. Please try again."

    # return output.content
    return f"files generated: {output_files}\ncode output: {output.content}"



class LocalCodeBoxToolRunManager:
    _instance = None

    codebox: LocalBox | CodeBox
    input_files: list[File]
    output_files: list[File]
    code_log: list[tuple[str, str]]
    verbose: bool

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.codebox = CodeBox()
            cls._instance.codebox.start()
            cls._instance.input_files = []
            cls._instance.output_files = []
            cls._instance.code_log = []
            cls._instance.verbose = True
        return cls._instance

    @classmethod
    def _run_handler(cls, code: str) -> str:
        """Run code in container and send the output to the user"""


        self = cls.instance()
        print(f"Code box obj ID: {id(self.codebox)}")
        print(f"Code box session ID: {self.codebox.session_id}")
        print("Code:\n", code)
        output: CodeBoxOutput = self.codebox.run(code)
        self.code_log.append((code, output.content))

        if not isinstance(output.content, str):
            raise TypeError("Expected output.content to be a string.")

        if output.type == "image/png":
            filename = f"image-{uuid4()}.png"
            file_buffer = BytesIO(base64.b64decode(output.content))
            file_buffer.name = filename
            self.output_files.append(File(name=filename, content=file_buffer.read()))
            return f"Image {filename} got send to the user."

        elif output.type == "error":
            if "ModuleNotFoundError" in output.content:
                if package := re.search(
                    r"ModuleNotFoundError: No module named '(.*)'",
                    output.content,
                ):
                    self.codebox.install(package.group(1))
                    return (
                        f"{package.group(1)} was missing but "
                        "got installed now. Please try again."
                    )
            else:
                # TODO: pre-analyze error to optimize next code generation
                pass
            if self.verbose:
                print("Error:", output.content)

        # elif modifications := get_file_modifications(code, self.llm):
        #     for filename in modifications:
        #         if filename in [file.name for file in self.input_files]:
        #             continue
        #         fileb = self.codebox.download(filename)
        #         if not fileb.content:
        #             continue
        #         file_buffer = BytesIO(fileb.content)
        #     file_buffer.name = filename
        #     self.output_files.append(
        #         File(name=filename, content=file_buffer.read())
        #     )

        return output.content


class CodeInput(BaseModel):
    code: str = Field(description="The code to run in the codebox.")


local_codebox_tool = StructuredTool(
    name="localcodebox",
    description=TOOL_DESCRIPTION,
    func=LocalCodeBoxToolRunManager._run_handler,
    args_schema=CodeInput,  # type: ignore
)

__all__ = ("local_codebox_tool",)
