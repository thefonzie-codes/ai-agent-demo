# imports

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

from db import generate_db


def call_gemini_api(query):
    """
    We do NOT want to place the API key in the code.  Leaving it in the code allows others to view the key.
    And if you're paying for that API key, and the cost increases based on usage - well, that won't be fun for you.
    Instead, it's placed in the environment, or a dotfile.  Dotfiles are hidden by default.
    We use a '.env' file to store configuration settings, environment variables etc.
    Basically, this is sensitive information, securely.
    """
    try:
        load_dotenv() #This loads the .env file
    except e:
        raise Exception(e)
    
    """
    Try/Except:
    This is what we call 'error handling' - it is a way to deal with errors without crashing the program.
    Basically, whatever happens in the 'try' block runs, and if something goes wrong, 
    it skips right to the 'except' block.
    """

    # This calls the Gemini API
    try:
        client = genai.Client() #The API key located in the env file is found and automatically used
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query
        )
        return response.text
    except e:
        raise Exception(e)

def manage_chats():
  pass

def read_db():
  conn = sqlite3.connect('customer_db.db')
  cursor = conn.cursor()
  cursor.execute()

def main():
  print("Generating Mock Customer Data...")
  generate_db()
  print("Hi! How can I help today?")
  query = input()

  print(call_gemini_api(query))

if __name__ == "__main__":
  main()