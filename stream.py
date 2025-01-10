import sys, os, json
import requests as req
from urllib.parse import urlparse, urlunparse


def main(argv):
    #print(argv)
    #argv=['stream/demo']
    url = urlparse(os.getenv("OPSDEV_APIHOST"))
    netloc = f"stream.{url.netloc}"
    path = f"/web/{os.getenv("OPSDEV_USERNAME")}/{argv[0]}"
    streamer = urlunparse(url._replace(netloc=netloc, path=path))
    msg =  {"input": " ".join(argv[1:])} if len(argv)>1 else {}
    lines = req.post(streamer, json=msg, stream=True).iter_lines()
    for line in lines:
        #line = next(lines)
        msg = json.loads(line.decode("utf-8")).get("output", "")
        if msg != "":
            print(msg, end="", flush=True)            
        else: 
            print()
            break
   
if __name__ == "__main__":
    main(sys.argv[1:])
