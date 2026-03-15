# --- 1. IMPORTS ---
import os
import fitz
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- 2. CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

# --- 3. SETUP ---
client = genai.Client(api_key=api_key)
conversation_history = []

# --- 4. PDF LOADER ---
def load_pdf(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        exit(1)

    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    print(f"PDF loaded: '{file_path}' ({len(doc)} pages)\n")
    doc.close()
    return full_text

# --- 5. INITIALIZE DATA ---
pdf_text = load_pdf("document.pdf")
SYSTEM_PROMPT = "You are a helpful assistant. Answer questions based only on the context provided to you: "

# --- 6. CHUNKING ---
def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

chunks = chunk_text(pdf_text)
print(f"Document split into {len(chunks)} chunks\n")

# --- 7. EMBEDDINGS ---
def get_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-exp-03-07",
        contents=text
    )
    return response.embeddings[0].values

def embed_all_chunks(chunks):
    print("Embedding chunks... (this may take a moment)\n")
    embedded = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        embedded.append({
            "text": chunk,
            "embedding": embedding
        })
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(chunks)} chunks embedded...")

    print(f"All {len(chunks)} chunks embedded successfully\n")
    return embedded

# --- 8. CHAT LOGIC ---
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

# --- 9. MAIN INTERFACE ---
print("Chatbot ready. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    
    response = chat(user_input)
    print(f"Bot: {response}\n")
