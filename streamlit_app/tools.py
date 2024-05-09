from codeboxapi import CodeBox
from langchain_core.tools import tool
from uuid import uuid4
from io import BytesIO
import base64


@tool
def codeboxtool(code: str) -> str:
    "input a string of code to an ipython interpeter, and get the result back."
    "Remember to always use double quotes only when generating json."
    "The start of the result will be list of files generated, then any printed text will be shown."

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
