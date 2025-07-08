import os, json, datetime, markdown, time, threading, sys, queue
import pathlib
from google import genai
from google.genai import types

APIkeys = {
    "gemini": "AIzaSyBQ5omYYQv5T0gmD2wOq19iyqC-02GahJ4"
}
# thing to replace in prompt with: thing to replace in prompt
promptReplacements = {
    "Game Descriptions": "gameDescription",
    "Files Descriptions": "filesDescription"
}


def userInputYN(userPrompt):
    userInput = ''
    while (userInput != 'y') and (userInput != 'n'):
        userInput = customInput(f"{userPrompt} 'y' / 'n': ").lower()
    return userInput


def customInput(userPrompt):
    userInput = input(userPrompt)
    if (userInput.lower() == "exit") or (userInput.lower() == "quit"):
        exit()
    return userInput


# make default files
if not os.path.exists("savedData.json"):
    tempFile = open("savedData.json", 'w')
    json.dump({
        "Prompts": {
            "Default": "These are documents containing level data (filesDescription). gameDescription Among the levels without survivorship bias, which levels do players like and dislike? Among the levels with survivorship bias, which levels do players like and dislike? Make your own algorithm to decide when survivorship bias occurs based on when the spread of player drop-off rates stabilizes. Compared to other levels, why are these levels liked or disliked? Based on the correlations between various data points, are there any insights on player behavior based on the contents of each level and features introduced in the progression map? After this, provide a concise response about actionable insights to the gameâ€™s developers. Separate sections for players with/without survivorship bias with subsections for what the game developers should add/remove/improve/rework. Throughout your response, make connections to the features of similar games through research."
        },
        "Files Descriptions": {
            "Default": '''"RAW Game Data Sheets - Level Data.csv": contents of each level || "RAW Game Data Sheets - Progression Map.csv": progression map across levels || "RAW Game Data Sheets - Raw Analysis Data.csv": raw player data for each level'''
        },
        "Game Descriptions": {
            "Word Nut": "This is for a casual mobile game in which players must sort jumbled characters to form words in a crossword puzzle."
        }
    }, tempFile, indent=2)
    tempFile.close()
    print('Created file "savedData.json"')

# load from 'savedData.json' for modification/extraction of entries
tempFile = open("savedData.json", 'r')
savedData: dict = json.load(tempFile)
tempFile.close()


# selects/overwrites/creates entries in a dictionary through user input. also displays but prevents the selection of invalid entries and their reasons.
def entryProcess(entries: dict, userEntry):
    print('')
    selectedEntryName = ""

    while selectedEntryName not in entries:
        for entry in entries:
            print(f"{entry}: {entries[entry]}")
        selectedEntryName = customInput("Select an entry above or make a new entry: ")
        if (selectedEntryName[:6].lower() == "remove") and (selectedEntryName[7:] in entries.keys()):
            userInput = userInputYN(f'Remove entry {selectedEntryName[7:]}?')
            if userInput == 'y':
                entries.pop(selectedEntryName[7:])
            print('')
        elif selectedEntryName not in entries:
            userInput = userInputYN("Create new entry?")
            if userInput == 'y':
                if userEntry == "Files Descriptions":
                    filesDesc = ""
                    if os.listdir("filesForAnalysis"):
                        for ffa in os.listdir("filesForAnalysis"):
                            ffaDesc = ""
                            while ffaDesc == "":
                                ffaDesc = customInput(f'Enter a brief description for the file "{ffa}": ')
                            filesDesc += f'"{ffa}": {ffaDesc} || '
                        filesDesc = filesDesc[:-4]
                        entries.update({selectedEntryName: filesDesc})
                    else:
                        raise FileNotFoundError("filesForAnalysis cannot be empty!")
                else:
                    while True:
                        tempInput = customInput(f'Enter contents of "{selectedEntryName}": ')
                        if tempInput.split(' ')[0] == "INVALID":
                            print('Cannot start with "INVALID"!')
                            continue
                        break
                    print('')
            selectedEntryName = ""
            print('')
        elif savedData[userEntry][selectedEntryName].split(' ')[0] == "INVALID":
            customInput(f"{savedData[userEntry][selectedEntryName]} (press ENTER to continue)")
            selectedEntryName = ''
            print('')
            continue
    print('')
    return {selectedEntryName: entries[selectedEntryName]}, entries


# make default folders
createDirs = ["filesForAnalysis", "templates/responses"]
for d in createDirs:
    if not os.path.exists(d):
        os.mkdir(d)
        print(f'Created directory "{d}"')

# possible MIME types for Gemini
mimetypes = {"pdf": "application/pdf", "txt": "text/plain", "html": "text/html", "csv": "text/csv", "xml": "text/xml"}


class Main:
    def __init__(self):
        self.responses = {}
        self.runs = 0
        self.prompt = ""
        self.selectedData = {}
        for k in savedData:
            self.selectedData.update({k: {}})
        self.invalidData = {}

    def export(self):
        tempData = {}
        for k in savedData:
            tempData.update({k: {}})
            for e in savedData[k]:
                if savedData[k][e].split(' ')[0] == "INVALID":
                    tempData[k].update({e: self.invalidData[k][e]})  # load from saved invalid data
                else:
                    tempData[k].update({e: savedData[k][e]})  # load from user entry
        print('Progress saved in "savedData.json"')
        tempFile = open("savedData.json", 'w')
        json.dump(tempData, tempFile, indent=2)
        tempFile.close()

    def queryGemini(self):
        print("Querying...")
        gemini = genai.Client(api_key=APIkeys["gemini"])
        contents = [types.Part.from_bytes(data=pathlib.Path(doc.path).read_bytes(), mime_type=mimetypes[doc.path.split('.')[-1]]) for doc in os.scandir("filesForAnalysis")]  # prepare files in filesForAnalysis
        contents.append(self.prompt)
        self.responses["gemini"] = gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(include_thoughts=True))  # include thinking in response
        )

    def updateInvalidEntries(self):
        self.invalidData = {}
        for k in savedData:
            self.invalidData.update({k: {}})
        for fd in savedData["Files Descriptions"]:
            missingFileDesc = ""
            for f in savedData["Files Descriptions"][fd].split(" || "):
                f = f.split(": ")[0][1:-1]
                if f not in os.listdir("filesForAnalysis"):
                    missingFileDesc += f'"{f}", '
            missingFileDesc = missingFileDesc[:-2]
            if missingFileDesc != "":
                self.invalidData["Files Descriptions"].update({fd: savedData["Files Descriptions"][fd]})
                savedData["Files Descriptions"].update({fd: f"INVALID (Missing file(s): {missingFileDesc})"})

    def main(self):
        self.updateInvalidEntries()
        if self.runs > 0:
            print("\n\n")
        self.responses = {}
        for modelName in APIkeys:
            self.responses.update({modelName: ""})
        userIdx = -1
        while (userIdx != 0) or any(e == {} for e in self.selectedData.values()):
            print('')
            for i, k in enumerate(savedData.keys()):
                print(f"{i + 1}: {k} -- {list(self.selectedData[k].keys())[0] if self.selectedData[k] else "*NOT CHOSEN*"}")
            try:
                userIdx = int(customInput('Select an entry above or enter "0" to query the AI: '))
            except ValueError:
                continue
            if (userIdx > 0) and (userIdx <= len(savedData)):
                userEntry = list(savedData.keys())[userIdx - 1]
                self.selectedData[userEntry], savedData[userEntry] = entryProcess(savedData[userEntry], userEntry)
        self.export()
        self.saveResponse()

    def preparePrompt(self):
        for k in self.selectedData:
            for e in self.selectedData[k]:
                while '\n' in self.selectedData[k][e]:
                    self.selectedData[k][e].replace('\n', ' ')
        self.prompt = list(self.selectedData["Prompts"].values())[0]
        for p in promptReplacements:
            self.prompt = self.prompt.replace(promptReplacements[p], list(self.selectedData[p].values())[0])

    def saveResponse(self):
        self.preparePrompt()
        geminiQuerier = threading.Thread(target=self.queryGemini)
        stopwatchThread = threading.Thread(target=self.stopwatch)
        stopwatchThread.start()
        geminiQuerier.start()
        geminiQuerier.join()

        # parse and output each AI response for human reading
        currentTime = str(datetime.datetime.now()).replace(':', '-').replace(' ', '_')[:-7]
        for modelName in self.responses:
            os.mkdir(f"templates/responses/response--{currentTime}")
            if modelName == "gemini":
                for part in self.responses[modelName].candidates[0].content.parts:
                    if not part.text:
                        continue
                    if part.thought:
                        outFile = open(f"templates/responses/response--{currentTime}/{modelName}-thinking.html", 'w', encoding="utf-8", errors="xmlcharrefreplace")
                        outFile.write(markdown.markdown(part.text))
                        outFile.close()
                    else:
                        outFile = open(f"templates/responses/response--{currentTime}/{modelName}-response.html", 'w', encoding="utf-8", errors="xmlcharrefreplace")
                        outFile.write(markdown.markdown(part.text))
                        outFile.close()

        print(f'\nComplete! Check "responses/response--{currentTime}".')
        self.runs += 1

    def stopwatch(self):
        print('')
        timeElapsed: float = 0
        while any(r == "" for r in self.responses.values()):
            sys.stdout.write(f"\rQuerying... {timeElapsed:.2f}s")
            sys.stdout.flush()
            time.sleep(0.25)
            timeElapsed += 0.25

# Main().main()
