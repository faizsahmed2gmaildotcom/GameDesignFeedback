# Gemini API key: AIzaSyBQ5omYYQv5T0gmD2wOq19iyqC-02GahJ4
# DeepSeek API key: sk-fc9ce287f9b64e1baf4da34e365d3c2d
from google import genai
from openai import OpenAI

APIkeys = {
    "gemini": "AIzaSyBQ5omYYQv5T0gmD2wOq19iyqC-02GahJ4",
    "deepseek": "sk-fc9ce287f9b64e1baf4da34e365d3c2d"
}


class AI:
    def __init__(self, modelName, textContents: str | None = None):
        self.modelName = modelName.split('-')[0]
        if self.modelName == "gemini":  # use the Gemini API
            self.modelInstance = genai.Client(api_key=APIkeys[self.modelName])
        else:  # use the OpenAI API
            self.modelInstance = OpenAI(api_key=APIkeys[self.modelName], base_url="https://api.deepseek.com")


deepseek = OpenAI(api_key=APIkeys["deepseek"], base_url="https://api.deepseek.com/v1")
testDeepseekResponse = deepseek.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}
    ],
    stream=False
)

gemini = genai.Client(api_key="AIzaSyBQ5omYYQv5T0gmD2wOq19iyqC-02GahJ4")
testGeminiResponse = gemini.models.generate_content(
    model="gemini-2.5-flash",
    contents="Why is Zenless Zone Zero considered a 'gooner game'?"
)

deepseek = OpenAI(api_key="sk-fc9ce287f9b64e1baf4da34e365d3c2d", base_url="https://api.deepseek.com")

print(testGeminiResponse.text)
myAI = AI('based')
