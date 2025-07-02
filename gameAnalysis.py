import os, json, datetime, markdown, time
import pathlib
from google import genai
from google.genai import types

APIkeys = {
    "gemini": "AIzaSyBQ5omYYQv5T0gmD2wOq19iyqC-02GahJ4"
}

# make default files
if not os.path.exists("savedData.json"):
    tempFile = open("savedData.json", 'w')
    json.dump({
        "Prompts": {
            "Default": "These are documents containing level data (filesDescription). gameDescription Among the levels without survivorship bias, which levels do players like and dislike? Among the levels with survivorship bias, which levels do players like and dislike? Make your own algorithm to decide when survivorship bias occurs based on when the spread of player drop-off rates stabilizes. Compared to other levels, why are these levels liked or disliked? Based on the correlations between various data points, are there any insights on player behavior based on the contents of each level and features introduced in the progression map? After this, provide a concise response about actionable insights to the gameâ€™s developers. Separate sections for players with/without survivorship bias with subsections for what the game developers should add/remove/improve/rework. Throughout your response, make connections to the features of similar games through research."
        },
        "Files Descriptions": {
            "Default": '''"RAW Game Data Sheets - Level Data.csv": contents of each level, "RAW Game Data Sheets - Progression Map.csv": progression map across levels, "RAW Game Data Sheets - Raw Analysis Data.csv": raw player data for each level'''
        },
        "Game Descriptions": {
            "Word Nut": "This is for a casual mobile game in which players must sort jumbled characters to form words in a crossword puzzle."
        }
    }, tempFile, indent=2)
    tempFile.close()
    print('Created file "savedData.json"\n')

# load from 'savedData.json' for modification/extraction of entries
tempFile = open("savedData.json", 'r')
savedData = json.load(tempFile)
tempFile.close()


# selects/overwrites/creates entries in a dictionary through user input
def entryProcess(entries: dict):
    print('')
    selectedEntryName = ""
    while selectedEntryName not in entries.keys():
        for entry in entries:
            print(f"{entry}: {entries[entry]}")
        selectedEntryName = input("Select an entry above or make a new entry: ")
        if (selectedEntryName.split(' ')[0].lower() == "remove") and (selectedEntryName[7:] in entries.keys()):
            print('')
            entries.pop(selectedEntryName[7:])
        elif selectedEntryName == '':
            print('')
            continue
        elif selectedEntryName not in entries.keys():
            userInput = ''
            while (userInput != 'y') and (userInput != 'n'):
                userInput = input("Create new entry? 'y' / 'n': ").lower()
            if userInput == 'y':
                if list(savedData.keys())[userSelection - 1] == "Files Descriptions":
                    filesDesc = ""
                    for ffa in os.scandir("filesForAnalysis"):
                        ffaDesc = ""
                        while ffaDesc == "":
                            ffaDesc = input(f'Enter a brief description for the file "{ffa.name}": ')
                        filesDesc += f'"{ffa.name}": {ffaDesc}, '
                    filesDesc = filesDesc[:-2]
                    entries.update({selectedEntryName: filesDesc})
                else:
                    entries.update({selectedEntryName: input(f'Enter contents of "{selectedEntryName}": ')})
                    print('')
            selectedEntryName = ""
            print('')
    print('')
    return selectedEntryName, entries


# make default folders
createDirs = ["filesForAnalysis", "responses"]
for d in createDirs:
    if not os.path.exists(d):
        os.mkdir(d)
        print(f'Created directory "{d}"')

responses = {}
for modelName in APIkeys:
    responses.update({modelName: ""})

# possible MIME types for Gemini
mimetypes = {"pdf": "application/pdf", "txt": "text/plain", "html": "text/html", "csv": "text/csv", "xml": "text/xml"}

# query Gemini
selectedData = {}
selectedEntryNames = []
for k in savedData:
    selectedData.update({k: ""})
    selectedEntryNames.append("")
userSelection = -1
while (userSelection != 0) or any(e == "" for e in selectedData.values()):
    print('')
    for i, k in enumerate(savedData.keys()):
        print(f"{i + 1}: {k} -- {selectedEntryNames[i] if selectedData[k] else "*NOT CHOSEN*"}")
    try:
        userSelection = int(input('Select an entry above or enter "0" to query the AI: '))
    except ValueError:
        continue
    if (userSelection > 0) and (userSelection <= len(savedData)):
        selectedEntryNames[userSelection - 1], savedData[list(savedData.keys())[userSelection - 1]] = entryProcess(savedData[list(savedData.keys())[userSelection - 1]])
        selectedData[list(savedData.keys())[userSelection - 1]] = savedData[list(savedData.keys())[userSelection - 1]][selectedEntryNames[userSelection - 1]]
tempFile = open("savedData.json", 'w')
json.dump(savedData, tempFile, indent=2)
tempFile.close()

prompt = selectedData["Prompts"].replace("filesDescription", selectedData["Files Descriptions"]).replace("gameDescription", selectedData["Game Descriptions"])

gemini = genai.Client(api_key=APIkeys["gemini"])
contents = [types.Part.from_bytes(data=pathlib.Path(doc.path).read_bytes(), mime_type=mimetypes[doc.path.split('.')[-1]]) for doc in os.scandir("filesForAnalysis")]  # prepare files in filesForAnalysis
contents.append(prompt)
responses["gemini"] = gemini.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(include_thoughts=True))  # include thinking in response
)
# do something here while waiting for response (ask copilot and look up how to run more lines of code while querying Gemini)

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

print(f"\nComplete! Check 'responses/response#{currentTime}'.")
