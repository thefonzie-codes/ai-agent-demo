# imports

from google import genai
from google.genai import types
from dotenv import load_dotenv
import datetime
import sys
from db import generate_db, delete_db, query_db

schema = open("./sample_datasets/travel_company_customer_db/schema.sql", "r").read()

query_db_declaration = {
    "name": "query_db",
    "description": "Searches the sqlite 3 database and returns a tuple of the values requested",
    "parameters": {
        "type": "object",
        "properties": {
            "sqlite3_query": {
                "type": "string",
                "description": f"""
                An SQLITE3 query to search the database. This is the current schema:
                {schema}
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
        tools = types.Tool(function_declarations=[query_db_declaration])
        
        # Add system instructions here
        system_instruction = """
        You are a helpful assistant for customer support.  Customer support agents will ask you questions about the database and you will help them.
        
        Be friendly, professional, and always verify information from the database before responding.
        If you need to query the database, use the query_db function.
        """
        
        config = types.GenerateContentConfig(
            tools=[tools],
            system_instruction=system_instruction
        )
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

        if response.candidates[0].content.parts[0].function_call:
            tool_call = response.candidates[0].content.parts[0].function_call
            if tool_call.name == "query_db":
                result = query_db(tool_call.args['sqlite3_query'])
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

print("Generating Mock Travel Company Customer Data...")
generate_db("./sample_datasets/travel_company_customer_db/travel_company.db")
chats = []
print("Hi! How can I help today?")
user_query = ""
while user_query != "exit":
    user_query = f"User: {input()}"
    if "exit" in user_query.lower():
        print("Goodbye!")
        sys.exit()
    else:
        print("Thinking...")
    response = call_gemini_api(user_query)
    print(f"� Agent: {response}")
    chats.append(user_query)
    chats.append(response)

with open(f"./chat_logs/{datetime.datetime.now()}", "a") as f:
    f.write("".join(chats))

if __name__ == "__main__":
    main()
