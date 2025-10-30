from google import genai
from google.genai import types

class Agent: 
    
    def __init__(models: [] = ["gemini-2.5-flash"], tools: [] = [], system_instruction: str = ""):
        self.client = genai.Client()
        self.config = types.GenerateContentConfig(
            tools=[tools],
            system_instruction=system_instruction
        )
        if len(models) == 0:
            print("No models provided... using default model")
            models = ["gemini-2.5-flash"]
        self.models = models
        self.tools = types.Tool(function_declarations=tools)

    def call(prompt):
        self.client.models.generate_content(
            model = self.models[0],
            contents = prompt,
            config = self.config,
        )