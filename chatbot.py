import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# LOAD CONFIG
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    print("Please create a .env file with: GEMINI_API_KEY=your_api_key_here")
    exit(1)

# SETUP

client = genai.Client(api_key=api_key)
conversation_history = []

SYSTEM_PROMPT = "You are a helpful assistant."

# CHAT FUNCTION

def chat(user_message):
    conversation_history.append(
        types.Content(role="user", parts=[types.Part(text=user_message)])
    )

    response = client.models.generate_content(
        model="gemini-flash-latest",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        contents=conversation_history
    )

    assistant_message = response.text

    conversation_history.append(
        types.Content(role="model", parts=[types.Part(text=assistant_message)])
    )

    return assistant_message

# Run it
print("Chatbot ready. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    response = chat(user_input)
    print(f"Bot: {response}\n")