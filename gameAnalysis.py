import os
import datetime
from google import genai
from google.genai import types
import markdown

dirs = ["filesForAnalysis", "responses"]
for d in dirs:
    if not os.path.exists(d):
        os.mkdir(d)

currentTime = str(datetime.datetime.now()).replace(':', '-').replace(' ', '_')[:-7]

showThinking = True
query = "Intricately explain the problems with the open-world gacha RPG Genshin Impact to a game developer."
APIkeys = {
    "gemini": "AIzaSyBQ5omYYQv5T0gmD2wOq19iyqC-02GahJ4"
}

responses = {}
for modelName in APIkeys.keys():
    responses.update({modelName: ""})

# query gemini
gemini = genai.Client(api_key=APIkeys["gemini"])
responses["gemini"] = gemini.models.generate_content(
    model="gemini-2.5-flash",
    contents=query,
    config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(include_thoughts=True))  # include thinking in response
)

# format each AI response for human reading
for modelName in responses.keys():
    os.mkdir(f"responses/log#{currentTime}")
    if modelName == "gemini":
        for part in responses[modelName].candidates[0].content.parts:
            if not part.text:
                continue
            if part.thought and showThinking:
                outFile = open(f"responses/log#{currentTime}/{modelName}-thinking.html", 'w', encoding="utf-8", errors="xmlcharrefreplace")
                outFile.write(markdown.markdown(part.text))
                outFile.close()
            else:
                outFile = open(f"responses/log#{currentTime}/{modelName}-response.html", 'w', encoding="utf-8", errors="xmlcharrefreplace")
                outFile.write(markdown.markdown(part.text))
                outFile.close()
