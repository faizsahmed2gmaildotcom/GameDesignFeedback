import os, json, datetime, markdown
import pathlib
from google import genai
from google.genai import types

APIkeys = {
    "gemini": "AIzaSyBQ5omYYQv5T0gmD2wOq19iyqC-02GahJ4"
}

# make default files
if not os.path.exists("config.json"):
    tempFile = open("config.json", 'w')
    json.dump({"specific": {"filesDescription": "", "gameDescription": ""}, "general": {"prompt": "", "extraContext": ""}}, tempFile, indent=2)
    tempFile.close()

# load data from 'config.json'
tempFile = open("config.json", 'r')
config = json.load(tempFile)
tempFile.close()
# check that nothing under 'specific' in 'config.json' is empty
for cbe in config["specific"]:
    while config["specific"][cbe] == "":
        if cbe == "filesDescription":
            for fileForAnalysis in os.scandir("filesForAnalysis"):
                fileDesc = ""
                while fileDesc == "":
                    fileDesc = input(f'MISSING: Enter brief description for "{fileForAnalysis.name}": ')
                config["specific"][cbe] += f"'{fileForAnalysis.name}': {fileDesc}, "
            config["specific"][cbe] = config["specific"][cbe][:-2]
        else:
            config["specific"][cbe] = input(f"MISSING: '{cbe}' in config.json. Check the ReadMe and its value here: ")
tempFile = open("config.json", 'w')
json.dump(config, tempFile, indent=2)
tempFile.close()

# make default folders
createDirs = ["filesForAnalysis", "responses"]
for d in createDirs:
    if not os.path.exists(d):
        os.mkdir(d)

responses = {}
for modelName in APIkeys:
    responses.update({modelName: ""})

# possible MIME types for Gemini
mimetypes = {"pdf": "application/pdf", "txt": "text/plain", "html": "text/html", "csv": "text/csv", "xml": "text/xml"}

# query Gemini
gemini = genai.Client(api_key=APIkeys["gemini"])
contents = [types.Part.from_bytes(data=pathlib.Path(doc.path).read_bytes(), mime_type=mimetypes[doc.path.split('.')[-1]]) for doc in os.scandir("filesForAnalysis")]  # prepare files in filesForAnalysis
prompt = config["general"]["prompt"]
for s in config["specific"]:
    prompt = prompt.replace(s, config["specific"][s])
contents.append(prompt + config["general"]["extraContext"])
# print(contents)
responses["gemini"] = gemini.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(include_thoughts=True))  # include thinking in response
)

# format and output each AI response for human reading
currentTime = str(datetime.datetime.now()).replace(':', '-').replace(' ', '_')[:-7]
for modelName in responses.keys():
    os.mkdir(f"responses/response#{currentTime}")
    if modelName == "gemini":
        for part in responses[modelName].candidates[0].content.parts:
            if not part.text:
                continue
            if part.thought:
                outFile = open(f"responses/response#{currentTime}/{modelName}-thinking.html", 'w', encoding="utf-8", errors="xmlcharrefreplace")
                outFile.write(markdown.markdown(part.text))
                outFile.close()
            else:
                outFile = open(f"responses/response#{currentTime}/{modelName}-response.html", 'w', encoding="utf-8", errors="xmlcharrefreplace")
                outFile.write(markdown.markdown(part.text))
                outFile.close()

print("Complete! Check the 'responses' directory.")