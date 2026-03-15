# Chatbot Code Guide

This guide explains how `chatbot.py` works, line by line. Use this to understand the logic without cluttering your main code file.

---

## 1. Imports
```python
import os
import fitz
from google import genai
from google.genai import types
from dotenv import load_dotenv
```
- **`os`**: Helps Python talk to your operating system (like checking if a file exists).
- **`fitz`**: This is the library (PyMuPDF) used to read text from PDF files.
- **`genai` & `types`**: The official tools from Google to talk to Gemini AI.
- **`load_dotenv`**: Reads your `.env` file so your secret API key isn't stuck inside the code.

---

## 2. Configuration & API Key
```python
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```
- We load the environment variables and fetch the `GEMINI_API_KEY`.
- If the key is missing, we stop the program immediately with a helpful message.

---

## 3. Initial Setup
```python
client = genai.Client(api_key=api_key)
conversation_history = []
```
- **`client`**: This is our connection "hub" to Google.
- **`conversation_history`**: A list that stores every message. This gives the bot "memory" so it remembers what you said earlier.

---

## 4. Reading the PDF (`load_pdf` function)
- This function opens the PDF and loops through every page.
- It extracts the text from each page and joins it into one long string.
- It closes the file at the end to keep things tidy.

---

## 5. Initialize Data
```python
pdf_text = load_pdf("document.pdf")
SYSTEM_PROMPT = "You are a helpful assistant. Answer questions based only on the context provided to you: "
```
- We load the PDF text into a variable.
- **`SYSTEM_PROMPT`**: This defines the AI's core "instruction." We've simplified it here to tell the AI to stick only to the provided context.

---

## 6. Text Chunking (`chunk_text` function)
```python
while start < len(text):
    end = start + chunk_size
    chunks.append(text[start:end])
    start += chunk_size - overlap
```
- Large PDFs are too big for AI to read in one go. We split the text into smaller **chunks** (e.g., 500 characters).
- We use **overlap** so that if a sentence is cut in half, the next chunk captures the beginning of it, preventing lost context.

---

## 7. Embeddings & Mathematical Meaning
```python
def get_embedding(text):
    # Calls Gemini Embedding model
```
- **Embeddings**: This converts text into a long list of numbers. 
- These numbers represent the *mathematical meaning* of the text. This allows the computer to calculate which piece of text is most similar to your question.
- **`embed_all_chunks`**: This function runs at startup. it goes through every chunk of your PDF and converts it into numbers so they are ready for searching later.

---

## 8. Chat Logic (`chat` function)
- It adds your message to the `conversation_history`.
- It sends the history and the `SYSTEM_PROMPT` to Gemini.
- It receives the response, saves it to history, and returns the text.

---

## 9. Main Interface
- The `while True` loop keeps the program running.
- It waits for you to type `quit` to stop, otherwise, it handles the conversation.
