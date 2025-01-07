import sys, os, json
import requests as req
from urllib.parse import urlparse, urlunparse


def main(argv):
    #print(argv)
    url = urlparse(os.getenv("OPSDEV_APIHOST"))
    netloc = f"streamer.{url.netloc}"
    path = f"/web/{os.getenv("OPSDEV_USERNAME")}/{argv[0]}"
    streamer = urlunparse(url._replace(netloc=netloc, path=path))
    lines = req.get(streamer, stream=True).iter_lines()
    #print(streamer)
    for line in lines:
        #line = next(lines)
        #print(line)
        #continue
        msg = json.loads(line.decode("utf-8")).get("stream", "")
        if msg != "":
            print(msg, end="")
        else: 
            print()
            break
   
if __name__ == "__main__":
    main(sys.argv[1:])
