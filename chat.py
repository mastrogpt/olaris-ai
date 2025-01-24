import sys, os, os.path, json
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
        state = dic.get("state", state)
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
from prompt_toolkit.completion import Completer, Completion


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
    return {"form": res}

import boto3
from botocore.client import Config
from datetime import datetime

def upload(file):
    path = os.path.join(os.getenv("OPS_PWD"), text)
    print(path)
    if not os.path.exists(path):
        print(f"{file} does not exist")
        return None
    if not os.path.isfile(path):
        print(f"{file} is not a file")
        return None
    print(f"uploading {file}...", end='', flush=True)
    try:
        # connecting to s3
        url = os.getenv("S3_API_URL")
        key = os.getenv("S3_ACCESS_KEY")
        sec = os.getenv("S3_SECRET_KEY")
        cfg = Config(signature_version='s3v4')
        s3 = boto3.resource('s3', config=cfg, region_name='us-east-1',
            endpoint_url=url, aws_access_key_id=key, aws_secret_access_key=sec)
        
        current_time = datetime.now().strftime("%y-%m%d-%H%M%S")
        filename = os.path.basename(path)
        target = f"/upload/{current_time}/{filename}"
        bucket = os.getenv("S3_BUCKET_DATA")
        s3.Bucket(bucket).upload_file(path, target)
        print("done.")
        return target
    except Exception as e:
        print(str(e))
        return None

#def log(x):
#    with open("log.txt", "a") as f:
#        f.write(str(x))
#        f.write('\n')

import os.path
@bindings.add("tab")
def _(event):
    buf = event.app.current_buffer
    if buf.complete_state:
        text = buf.text[1:]
        path = os.path.join(os.getenv("OPS_PWD"), text)
        if os.path.isdir(path):
            buf.complete_state = None
            buf.start_completion(select_first=True)
        elif os.path.isfile(path):
            buf.complete_state = None
        else:
            buf.complete_next()
    else:
        buf.start_completion(select_first=True)

class FileCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("@"):
            #folder = os.path.dirname()
            path = f"{os.getenv("OPS_PWD")}/{text[1:]}"
            current_folder = os.path.dirname(path)
            prefix = os.path.basename(path)
            files = [file for file in os.listdir(current_folder) if file.startswith(prefix) ]
            for file in files:
                file = f"{file}/" if os.path.isdir(f"{current_folder}/{file}") else file
                yield Completion(file, start_position=-len(prefix))

completer = FileCompleter()

session = PromptSession(multiline=True, prompt_continuation=prompt_continuation, key_bindings=bindings, completer=completer)
print("Welcome to AI Chat. Exit with an empty line.\nEnd a line with a space for multiline input.\nStart with '@' to select a file to upload, press TAB to complete directory.")

curr = interact({})
while True:
    if "form" in curr:
        data = process_form(session, curr["form"])
        #print("Form:", json.dumps(res,indent=2))
        res = {"state": state, "input": data}
        curr = interact(res)
    else:
        text = session.prompt(f"{name}> ")
        if text.startswith("@"):
            text = text[1:]
            target = upload(text)
            if target:
                text = f"@{target}"
            else:
                print(f"cannot upload {text}")
                continue
        if text.strip() == '':
            print("Goodbye!")
            break
        curr = interact({"input":text, "state": state})
