import sys
import pymupdf
import nltk
from pathlib import Path
import subprocess
import json

import nltk.data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from nltk.tokenize import sent_tokenize

USAGE="pdf2txt (<action>|-) <file>..."

def parse_pdf(file):
    #print("*** parsing ", file)
    doc = pymupdf.open(file)
    i = 0
    out = ""
    for page in doc:
        #page = list(doc)[i]
        i+=1
        text = page.get_text()
        sentences = sent_tokenize(text)
        enum = enumerate(sentences, 1)
        for j, sentence in enum :
            #_, sentence = next(enum)
            sent = " ".join(sentence.split())
            if sent == ".": continue
            out += f"{sent}\n"
            #print(f"{i}.{j}\t{sent}\n")
    res = f"{file}.txt" 
    Path(res).write_text(out)
    print("saved", res)
    return res

def upload_text(action, filename):
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            #print(line.strip())            
            print(".", end="", flush=True)
            res = None
            try:
                msg = {"input": line.strip() }
                jof = f"{filename}.tmp"
                Path(jof).write_text(json.dumps(msg))
                cmd = ["ops", "invoke", action, "-P", jof, ]
                res = subprocess.run(cmd, check=True, capture_output=True)
            except Exception as e:
                print()
                print(cmd)
                if res:
                    print(res.stdout)
                    print(res.stderr)
                else:
                    print("ERROR", str(e))
        print()

def main(argv):
    #print(os.getcwd())
    if len(argv) < 1:
        print(USAGE)
        return
    action = argv[0]
    for filename in argv[1:]:
        if filename.endswith(".pdf"):
            print(">>> converting", filename)
            filename = parse_pdf(filename)
        if action != "-":
            print(">>> uploading", filename)
            upload_text(action, filename)


#print(sys.argv)
main(sys.argv[1:])