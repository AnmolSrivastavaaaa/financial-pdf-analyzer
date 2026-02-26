Financial PDF Analyzer
What this project is

This project is a simple backend tool that analyzes financial PDFs such as earnings call transcripts or management discussion sections.

The idea is straightforward:

You upload a PDF →
The system extracts the text →
An LLM analyzes the management commentary →
You get a structured financial summary in JSON format.

It’s designed as a focused research tool, not a chatbot.

Why I built it

Financial documents are long and dense. Instead of manually scanning through management commentary, this tool extracts the key signals automatically — tone, positives, concerns, guidance, and growth initiatives — in a structured format that’s easy to review.

The goal is clarity and usability, not flashy UI.

How it works

The user uploads a PDF file (max 5MB).

The system extracts text using pdfplumber.

The first ~12,000 characters are sent to a Groq LLM.

The model is instructed to:

Only extract explicitly mentioned information

Avoid assumptions or hallucinations

Return structured JSON

The response is parsed and returned through the API.

Everything runs through a FastAPI backend and can be tested using Swagger UI.

What the output looks like

The API returns structured JSON containing:

Tone of management (optimistic, cautious, etc.)

Confidence level

Key positives (3–5 points)

Key concerns (3–5 points)

Forward guidance

Capacity trends

Growth initiatives

If something isn’t mentioned in the PDF, the system explicitly says:
"Not mentioned in PDF"

This prevents guessing or fabricating information.

Tech stack

FastAPI (backend framework)

pdfplumber (PDF text extraction)

Groq API with llama-3.1-8b-instant

python-dotenv for secure API key handling

No frontend. Just a clean API-focused research tool.

How to run it

Install dependencies:

pip install fastapi uvicorn pdfplumber groq python-dotenv

Create a .env file in the root directory:

GROQ_API_KEY=your_secret_key_here

Start the server:

python -m uvicorn main:app --reload

Open:

http://127.0.0.1:8000/docs

Use the /analyze endpoint to upload a PDF.

Limitations

Only text-based PDFs are supported (no scanned/image PDFs).

Maximum file size is 5MB.

Only the first ~12,000 characters are sent to the model.

Output quality depends on how clearly the PDF text is structured.

Final Notes

This project focuses on practicality. It prioritizes structured, reliable output over complexity. It’s meant to function as a small internal research utility that extracts meaningful signals from management commentary in a consistent way.
