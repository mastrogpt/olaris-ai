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

USAGE="loader (<action>|-) <group> <collection> <file>..."

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

def post_text(text, collection, filename, action, options, verbose = False):
    res = None
    try:
        msg = {"input": text, "options": options, "state": collection }
        jof = f"{filename}.tmp"
        Path(jof).write_text(json.dumps(msg))
        cmd = ["ops", "invoke", action, "-P", jof, ]
        res = subprocess.run(cmd, check=True, capture_output=True)
        if verbose:
            try:
                print(json.loads(res.stdout.decode("utf-8")).get("body", {}).get("output", {}))
            except: 
                print(res.stdout.decode("utf-8"))
        return True
    except Exception as e:
        print("\nERROR:", str(e))
        print(cmd)
        if res:
            print(res.stdout)
            print(res.stderr)
        return False
            

def upload_text_by_lines(action, filename, group, collection, options):
    count = int(group)
    loop = True
    pos = 0
    with open(filename, "r", encoding="utf-8") as file:
        while loop:
            lines = []
            for n in range(0,count):
                try:
                    line = next(file)
                    lines.append(line.strip())
                    pos += 1
                except StopIteration:
                    loop = False
            #print(".", end="", flush=True)
            if len(lines) == 0:
                continue
            text = "\n".join(lines)
            if post_text(text, collection, filename, action, options):
                pos += 1
                print(pos, end=' ', flush=True)
            
        print()

def upload_text_by_size(action, filename, max, collection, options):
    lines = Path(filename).read_text().splitlines()
    n = nc = 0
    text = ""
    while n < len(lines):
        line = lines[n]
        n += 1
        if len(line.encode('utf-8')) > max:
            print(f"\nline {n} too long, skipping")
            continue
        if len(text.encode('utf-8')) + len(line.encode('utf-8')) > max:
            nc +=1
            #print(nc, len(text))
            end = '\n' if nc % 10 == 0 else ' '
            print(nc, f"[{len(text)}]", end=end, flush=True)
            if post_text(text, collection, filename, action, options):
                text = line
            else:
                print("Aborting...")
                return
        else:
            text += f"\n{line}"
    nc +=1
    post_text(text, collection, filename, action, options)
    print(f"\nRead {n} lines, sent {nc} chunk of max size {max}")

def main(argv):
    #print(argv)
    if len(argv) < 1:
        print(USAGE)
        return
    action = argv[0]
    maxsize = 4000
    try: maxsize = int(argv[1])
    except: pass
    collection = argv[2]
    options = argv[3]
    for filename in argv[4:]:
        print(filename)
        if filename.endswith(".pdf"):
            print(">>> converting", filename)
            filename = parse_pdf(filename)
        if action != "-":
            print("Action:", action, "MaxSize:", maxsize, "Collection:", collection, "Filename:", filename)
            upload_text_by_size(action, filename, maxsize, collection, options)

#print(sys.argv)
main(sys.argv[1:])