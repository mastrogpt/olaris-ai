import sys

from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

from openai import OpenAI
from dotenv import dotenv_values

# constants
ROLE="you are an helpful assistant"

## connecting
class Chat:

    messages = [ {"role": "system", "content": ROLE}]
    client = None
    model =  None

    def __init__(self, model):
        self.model = model
        token = dotenv_values().get("HUGGINGFACE_HUB_TOKEN")
        if not token:
            print("please put your HUGGINGFACE_HUB_TOKEN in .env")
            return 
        # Initialize the client, pointing it to one of the available models
        self.client = OpenAI(
            base_url="https://api-inference.huggingface.co/v1/",
            api_key=token,
        )

    def complete(self, message):
        self.messages.append({
            "role": "user",
            "content": message
        })
        #print(self.messages)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True,
            max_tokens=500
        )

        answer = ""
        for output in completion:
            chunk = output.choices[0].delta.content 
            answer += chunk
            print(chunk, end="")
        print()

        self.messages.append({
            "role": "assistant",
            "content":  answer
        })

## prompt
bindings = KeyBindings()

@bindings.add('enter')
def _(event):
    """
    When Enter is pressed, check if the current line is empty.
    If the line is empty, accept the input (i.e., end input).
    """
    buffer = event.app.current_buffer
    #print(buffer)
    if buffer.text=='.':
        buffer.validate_and_handle()  # Submit input

    if buffer.text.endswith('\n'):
        buffer.validate_and_handle()  # Submit input
    else:
        buffer.insert_text('\n')  # Continue to next line if not empty

def prompt_continuation(width, line_number, wrap_count):
    return f"{line_number+1}> "


MODELS = {
    "llama3-8": "meta-llama/Meta-Llama-3-8B-Instruct",
    "llama3-70": "meta-llama/Meta-Llama-3-70B-Instruct",
    "llama3": "meta-llama/Meta-Llama-3-70B-Instruct",
    "mixtral-8x7": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "mixtral": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "hermes-8x7": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
    "hermes": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
    "zephyr-7": "HuggingFaceH4/zephyr-7b-beta",
    "zephyr": "HuggingFaceH4/zephyr-7b-beta",
    "llama2-7": "meta-llama/Llama-2-7b-chat-hf",
    "lamma2-13": "meta-llama/Llama-2-13b-chat-hf",
    "lamma2": "meta-llama/Llama-2-13b-chat-hf",
    "mistral-7": "mistralai/Mistral-7B-Instruct-v0.2",
    "mistral": "mistralai/Mistral-7B-Instruct-v0.2",
    "cllama-7": "codellama/CodeLlama-7b-hf",
    "cllama-13": "codellama/CodeLlama-13b-hf",
    "cllama-34": "codellama/CodeLlama-34b-Instruct-hf",
    "cllama": "codellama/CodeLlama-34b-Instruct-hf",
}

def main(args):
    
    name = args[0][1:]

    if name == "list":
        print("Available models:")
        for k, v in MODELS.items():
            print(f"--{k} for {v}")
        sys.exit(0)

    if name == "":
        name = "llama3"
    if name in MODELS:
        model = MODELS[name]
    else:
        print(f"model {name} not avalable - use 'list' to see available models")
        sys.exit(0)

    chat = Chat(model)
    session = PromptSession(multiline=True, prompt_continuation=prompt_continuation, key_bindings=bindings)
    print("Welcome to AI Chat.\nTerminate input with an empty line or Meta+Enter.\nExit with '.'")
    while True:
        text = session.prompt(f"{name}> ")
        if text.strip() == '':
            print("Pardon?")
            continue
        if text == ".":
            print("Goodbye!")
            break
        chat.complete(text)


if __name__ == "__main__":
    main(sys.argv[1:])

"""
%load_ext autoreload
%autoreload 2
%cd scripts
import chat
chat.main([])
"""