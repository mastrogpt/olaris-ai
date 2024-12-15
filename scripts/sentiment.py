import sys

if len(sys.argv)==1:
    print("Usage: A='message'")
    sys.exit(0)

msg = " ".join(sys.argv[1:])
print(f"Message: {msg}")
from transformers import pipeline
print(pipeline('sentiment-analysis')(msg))
