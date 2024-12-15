import sys, requests, dotenv, re, os, argparse
from pathlib import Path

# Hugging Face Inference API endpoint for SDXL
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Retrieve Hugging Face API token
token = dotenv.dotenv_values().get("HFACE_API_TOKEN")
if not token:
    print("please put your HFACE_API_TOKEN in .env")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="generate an image from the description")
    parser.add_argument('--dir', type=str, help='The output file dir')
    parser.add_argument('--img', type=str, help='The source image')
    opt, args = parser.parse_known_args()

    # Define the payload (prompt), the headers and the image for the image generation
    global token, API_URL
    headers = { "Authorization": f"Bearer {token}" }
    prompt = " ".join(args)
    inputs = { "inputs": prompt }
    images = {"file": Path(opt.img).read_bytes()}
    #with open(opt.img, "rb") as image_file:
    #    image = image_file.read()

    # output file from the prompt
    out = re.sub(r'[^a-zA-Z0-9]+', '-', prompt)
    out = re.sub(r'-+', '-', out).strip('-')
    os.makedirs(opt.dir,  exist_ok=True)
    file = f"{opt.dir}/{out}.png"
 
    # Send the request to the Inference API
    print(f"Generating {file}...")

    response = requests.post(API_URL, headers=headers, json=inputs, files=images)

    # Check if the request was successful
    if response.status_code == 200:
        with open(file, "wb") as f:
            f.write(response.content)
        print(f"Image saved successfully as {file}")
    else:
        print(f"Failed to generate image: {response.status_code}, {response.text}")

if __name__ == "__main__":
    main()