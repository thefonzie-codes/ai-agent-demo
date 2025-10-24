# imports

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import sys
import datetime

from db import generate_db, delete_db, search_db

search_db_declaration = {
    "name": "search_db",
    "description": "Searches the sqlite 3 database and returns a tuple of the values requested",
    "parameters": {
        "type": "object",
        "properties": {
            "sqlite3_query": {
                "type": "string",
                "description": """
                An SQLITE3 query to search the database. This is the current schema:
                        CREATE TABLE IF NOT EXISTS customers (
                            id INTEGER PRIMARY KEY,
                            first_name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            phone TEXT NOT NULL,
                            issue TEXT NOT NULL
                        )
                        """,
            },
        },
        "required": ["sqlite3_query"],
    },
}

def call_gemini_api(user_query):    
    """
    Try/Except:
    This is what we call 'error handling' - it is a way to deal with errors without crashing the program.
    Basically, whatever happens in the 'try' block runs, and if something goes wrong, 
    it skips right to the 'except' block.
    """

    # This calls the Gemini API
    try:
        client = genai.Client() #The API key located in the env file is found and automatically used
        tools = types.Tool(function_declarations=[search_db_declaration])
        config = types.GenerateContentConfig(tools=[tools])
        contents = [
            types.Content(
                role="user", parts=[types.Part(text=user_query)]
            )
        ]
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config
        )
        # print(response.candidates[0].content.parts[0].function_call)
        if response.candidates[0].content.parts[0].function_call:
          tool_call = response.candidates[0].content.parts[0].function_call
          if tool_call.name == "search_db":
            result = search_db(tool_call.args['sqlite3_query'])
            print(f"TOOL CALL: {tool_call}")

          function_response_part = types.Part.from_function_response(
            name=tool_call.name,
            response={"result": result},
          )

          contents.append(response.candidates[0].content) # Append the content from the model's response.
          contents.append(types.Content(role="user", parts=[function_response_part])) # Append the function response

          client = genai.Client()
          final_response = client.models.generate_content(
              model="gemini-2.5-flash",
              config=config,
              contents=contents,
          )
          return(final_response.candidates[0].content.parts[0].text)
        # return(final_response.text)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(e)

def manage_chats():
  pass

def read_db():
  conn = sqlite3.connect('customer_db.db')
  cursor = conn.cursor()
  cursor.execute()

def main():
  """
  We do NOT want to place the API key in the code.  Leaving it in the code allows others to view the key.
  And if you're paying for that API key, and the cost increases based on usage - well, that won't be fun for you.
  Instead, it's placed in the environment, or a dotfile.  Dotfiles are hidden by default.
  We use a '.env' file to store configuration settings, environment variables etc.
  Basically, this is sensitive information, securely.
  """
  try:
      load_dotenv() #This loads the .env file
  except Exception as e:
      print(e)
      
  print("Generating Mock Customer Data...")
  generate_db()
  chats = []
  print("Hi! How can I help today?")
  user_query = ""
  while user_query != "exit":
    user_query = input()
    chats.append(f"🧑 User: {user_query}\n")
    context = "".join(chats)
    context += f"🧑 User: {user_query}\n"
    response = call_gemini_api(context)
    chats.append(f"🤖 Agent: {response}\n")
    print(response)

  with open(f"./chat_logs/{datetime.datetime.now()}", "a") as f:
    f.write("".join(chats))
  print("Deleting mock DB")
  delete_db("customer_db.db")

if __name__ == "__main__":
  main()