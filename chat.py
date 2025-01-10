import sys, os, json
import requests as req
from dotenv import dotenv_values
from urllib.parse import urlparse, urlunparse

if len(sys.argv) < 2:
    print("usage: <action> [<input>...]")
    sys.exit(0)

denv = dotenv_values(f"{os.getenv('OPS_PWD')}/.env") 
base = f"{os.getenv("OPSDEV_HOST")}/api/my"

# chat = "postgen"
chat = sys.argv[1]
name = chat
if chat.find("/") == -1:
    chat = f"{chat}/{chat}"

apiurl = urlparse(os.getenv("OPSDEV_APIHOST"))
netloc = f"stream.{apiurl.netloc}"
path = f"/web/{os.getenv("OPSDEV_USERNAME")}/{chat}"


# stremer and invoker entry points
streamer = urlunparse(apiurl._replace(netloc=netloc, path=path))
invoker = f"{base}/{chat}"

# streaming and state
streaming = False
state = ""

def interact(args):
    global streaming, state
    out = "no output provided"
    if streaming:
        lines = req.post(streamer, json=args, stream=True).iter_lines()
        out = ""
        for line in lines:
            #line = next(lines)
            #print(line)
            #continue
            dic = json.loads(line.decode("utf-8"))
            #print(dic)
            res = dic.get("output", "")
            state = dic.get("state", state)
            if res != "":
                out += res
                print(res, end="", flush=True)
            else: 
                print()
                break
        return {}
    else:
        dic = req.post(invoker, json=args).json()
        streaming = dic.get("streaming", False)
        out = dic.get("output", out)
        print(out)
        return dic

 
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
