from openai import OpenAI
from dotenv import dotenv_values
import sys

models = {
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


token = dotenv_values().get("HUGGINGFACE_HUB_TOKEN")
if not token:
    print("please put your HUGGINGFACE_HUB_TOKEN in .env")
    sys.exit(1)

model = sys.argv[1][1:]

if model == "list":
    print("Available models:")
    for k, v in models.items():
        print(f"--{k} for {v}")
    sys.exit(0)

if model == "":
    model = models["llama3-70"]
elif model in models:
    model = models[model]
else:
    print(f"model {model} not avalable - use 'list' to see available models")
    sys.exit(0)

msg = " ".join(sys.argv[2:])
if msg == "":
    print("Please provide some input")
    sys.exit(0)
    

# Initialize the client, pointing it to one of the available models
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/",
    api_key=token,
)

chat_completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": msg},
    ],
    stream=True,
    max_tokens=500,
)

# iterate and print stream
print(f">>> {msg}")
for message in chat_completion:
    print(message.choices[0].delta.content, end="")
print()
