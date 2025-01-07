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

def interact(dict):
    res = req.post(url, json=dict).json()
    while res.get("continue"):
        out = res.get("output")
        if out:
            print(out)
            del res["output"]
    return res
 
# input  = "Hello world"
if len(sys.argv) > 2:
   text = " ".join(sys.argv[2:])
   interact({"input": text})
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

def process_form(session, form):
    res = {}
    for entry in form:
        while True:
            if entry["type"] == "text":
                text = session.prompt(f"{entry['label']} ")
            elif entry["type"] == "textarea":
                text = session.prompt(f"{entry['label']} ", multiline=True)
            res[entry["name"]] = text
            if entry['required'] and text.strip() == '':
                print("This field is required, please enter a value.")
            else:
                break
    return res

session = PromptSession(multiline=True, prompt_continuation=prompt_continuation, key_bindings=bindings)
print("Welcome to AI Chat. Exit with an empty line.\nEnd a line with a space for multiline input.\n")

curr = interact({})
while True:
    state = curr.get("state", "")    
    if "form" in curr:
        res = process_form(session, curr["form"])
        print(res)
        res["state"] = state
        curr = interact(res)
    else:
        text = session.prompt(f"{name}> ")
        if text.strip() == '':
            print("Goodbye!")
            break
        curr = interact({"input":text, "state": state})
