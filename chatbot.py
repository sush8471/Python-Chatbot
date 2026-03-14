# --- IMPORT -------------------------------------------------------------------

# Bring in libraries we need: path checks, PDF reading, Gemini API, and secure environment config
import os
import fitz             # PyMuPDF, imported as fitz because that's its required name
from google import genai
from google.genai import types
from dotenv import load_dotenv


# --- LOAD CONFIG --------------------------------------------------------------

# Load environment variables from .env so we keep the API key out of the source code
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Stop early with a clear message if the key is missing, rather than letting it fail later
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    print("Please create a .env file with: GEMINI_API_KEY=your_api_key_here")
    exit(1)


# --- SETUP --------------------------------------------------------------------

# Create the connection object the Gemini API needs to send and receive messages
client = genai.Client(api_key=api_key)

# Store chat history as a list we will keep growing turn by turn to give the bot memory
conversation_history = []


# --- PDF LOADER FUNCTION ------------------------------------------------------

def load_pdf(file_path):
    """
    Read a PDF file and return all its text as one big string.
    This gives our chatbot the document context before any questions are asked.
    """
    # Make sure the PDF actually exists where we expect it, fail clearly if not
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        exit(1)

    # Open the PDF file so we can read its pages
    doc = fitz.open(file_path)
    
    # Build a full text string by adding each page's text one after another
    full_text = ""
    for page in doc:
        # Extract raw text from the current page and attach it to our growing string
        full_text += page.get_text()

    # Confirm the PDF loaded successfully and report size useful numbers
    print(f"PDF loaded: '{file_path}' ({len(doc)} pages, {len(full_text)} characters)\n")

    # Close the PDF object cleanly to free memory and avoid holding open handles
    doc.close()

    # Return the complete document text string to use in the system prompt
    return full_text


# --- LOAD PDF AT STARTUP ------------------------------------------------------

# Run the PDF loader once when the chatbot starts so the document is ready immediately
pdf_text = load_pdf("document.pdf")

# Build the system prompt with the PDF content included via an f-string
# This tells Gemini how to behave and what document it should answer based on
SYSTEM_PROMPT = f"""You are a helpful assistant. Answer questions based on this document:

{pdf_text}
"""


# --- CHAT FUNCTION ------------------------------------------------------------

def chat(user_message):
    """
    Send a user message to Gemini including the entire conversation history,
    save the reply, and return the bot's answer text.
    """
    # Add the current user message in Gemini’s required format (role plus text content)
    conversation_history.append(
        types.Content(role="user", parts=[types.Part(text=user_message)])
    )

    # Call Gemini with the system instruction, full history, and chosen model
    # The contents/history matters because it preserves memory across turns
    response = client.models.generate_content(
        model="gemini-flash-latest",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        contents=conversation_history
    )

    # Pull just the text reply out from the response object
    assistant_message = response.text

    # Add the assistant reply to history so future messages see what was said
    conversation_history.append(
        types.Content(role="model", parts=[types.Part(text=assistant_message)])
    )

    # Hand back the assistant’s answer string to the caller
    return assistant_message


# --- RUN IT -------------------------------------------------------------------

# Let the user know the chatbot is ready and explain how to exit
print("Chatbot ready. Type 'quit' to exit.\n")

# Loop forever, handling one input message at a time
while True:
    user_input = input("You: ")         # Pause and wait for the user to type something
    if user_input.lower() == "quit":    # Simple exit condition that works regardless of capitalization
        break                           # Leave the loop and end the program
    response = chat(user_input)         # Ask Gemini using our chat function and full history
    print(f"Bot: {response}\n")         # Show the bot’s reply in a clean readable line

