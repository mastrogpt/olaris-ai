from dotenv import dotenv_values
import sys, os, json
import requests as req

if len(sys.argv) < 2:
    print("usage: <action> [<input>...]")
    sys.exit(0)

denv = dotenv_values(f"{os.environ.get('OPS_PWD')}/.env") 
base = f"{os.environ.get("OPSDEV_HOST")}/api/my"

# chat = "postgen"
chat = sys.argv[1]
name = chat
if chat.find("/") == -1: 
    chat = f"{chat}/{chat}"

url = f"{base}/{chat}"


def interact(inp):
    res = req.post(url, json={"input": inp}).json()
    out = res.get("output")
    if out:
        print(out)
        del res["output"]
    if len(res.keys()) > 0:
        print(json.dumps(res, indent=2))

# input  = "Hello world"
if len(sys.argv) > 2:
   inp = " ".join(sys.argv[2:])
   interact(inp)
   sys.exit(0)


from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

## prompt
bindings = KeyBindings()

@bindings.add('enter')
def _(event):
    """
    When Enter is pressed, check if the current line ends with a space
    and continue the input, otherwise 
    If the line is empty, accept the input (i.e., end input).
    """
    buffer = event.app.current_buffer

    if buffer.text.endswith(' '):
        buffer.insert_text('\n')  # Continue to next line if not empty
        return

    buffer.validate_and_handle()

def prompt_continuation(width, line_number, wrap_count):
    return f"{line_number+1}> "

session = PromptSession(multiline=True, prompt_continuation=prompt_continuation, key_bindings=bindings)
print("Welcome to AI Chat. Exit with an empty line.\nEnd a line with a space for multiline input.\n")
while True:
    text = session.prompt(f"{name}> ")
    if text.strip() == '':
        print("Goodbye!")
        break
    interact(text)
