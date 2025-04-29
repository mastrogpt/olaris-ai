import sys, os
import yaml, requests
import os.path

BASE = "https://raw.githubusercontent.com/mastrogpt/mastrogpt-training/refs/heads/main"

def lessons():
    # download a file at BASE+/lessons assuming it is in yaml format
    # list the first level key as a list of lesson names
    res = requests.get(f"{BASE}/lessons.yaml")
    data = yaml.load(res.text, Loader=yaml.FullLoader)
    print("Available MastroGPT lessons:")
    for k in data.keys():
        print(" ", k)
    
def lesson(name, solution):
    # download a file at BASE+/lessons
    # get the entry corresponding to the lesson name
    # extract the list of the children under the entry as an array
    # download each file from BASE+file and save it locally
    # create any parent directory if needed
    # using as base $OPS_PWD
    res = requests.get(f"{BASE}/lessons.yaml")
    data = yaml.load(res.text, Loader=yaml.FullLoader)
    lesson = data[name]
    #name = "0=hello"
    print(f"Downloading {"solution " if solution else ''}files for lesson: {name}")
    for child in lesson:
        #child = lesson[0]
        
        # the child local file is the child + $OPS_PWD
        if solution:
            # if downloading the solution
            # skip all the file not ending with ".exercise"
            # download the file without .exercise as .solution
            if not child.endswith(".exercise"):
                continue
            src = f"{BASE}/{child[0:-len('.exercise')]}"
            tgt = f"{os.getenv("OPS_PWD")}/{child[0:-len('.exercise')]}.solution"
        else:
            # if a file ends as .exercise, download it without the .exercise extension
            src = f"{BASE}/{child}"
            if child.endswith(".exercise"):
                tgt = f"{os.getenv("OPS_PWD")}/{child[0:-len('.exercise')]}"
            else:
                tgt = f"{os.getenv("OPS_PWD")}/{child}"

        #print(src)
        if os.path.exists(tgt):
            print(f"Skipping {tgt} as it already exists")
            continue
        
        os.makedirs(os.path.dirname(tgt), exist_ok=True)
        try:
            with requests.get(src, stream=True) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                # Open a local file in binary write mode
                with open(tgt, "wb") as file:
                    # Write the response content to the file in chunks
                    for chunk in response.iter_content(chunk_size=8192):  # 8 KB chunks
                        if chunk:  # Avoid writing empty chunks
                            file.write(chunk)
            print(tgt)
        except Exception as e:
            print(f"Failed to download {src}: {str(e)}")
    
def main(args):
    if len(args) == 0:
        print("""usage:
    list
    lesson <name>
    solution <name>
""")
        sys.exit(0)
        
    if args[0] == "list": lessons()
    elif args[0] == "lesson": lesson(args[1], False)
    elif args[0] == "solution": lesson(args[1], True)
    else: main([])
    
if __name__ == "__main__":
    main(sys.argv[1:])
