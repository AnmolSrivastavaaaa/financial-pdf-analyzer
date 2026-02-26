from fastapi import FastAPI, UploadFile, File
from io import BytesIO
import json
import re
import pdfplumber
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Financial PDF Analyzer - Free Plan Safe")

# Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MAX_UPLOAD_MB = 5  # Free plan safe limit


def extract_text(file_bytes):
    """Extract text from a text-based PDF (no OCR)."""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text


def extract_json_from_response(content):
    """
    Safely extract JSON block from LLM response.
    Handles markdown fences and extra explanation text.
    """
    match = re.search(r'\{.*\}', content, re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # Read uploaded file
    contents = await file.read()

    # Check file size
    if len(contents) > MAX_UPLOAD_MB * 1024 * 1024:
        return {"error": f"File too large. Max allowed: {MAX_UPLOAD_MB} MB."}

    # Extract text
    text = extract_text(contents)
    if not text.strip():
        return {
            "error": (
                "Cannot extract text. Only text-based PDFs are supported. "
                "Scanned/image PDFs are NOT supported on free plan."
            )
        }

    # Prepare prompt for Groq
    prompt = f"""
You are a financial research assistant.

Only extract information explicitly mentioned in the PDF.
Do NOT assume or infer.
If something is missing, write "Not mentioned in PDF".

Return ONLY valid JSON.
Do not include explanations.
Do not wrap in markdown.

Required fields:
tone
confidence_level
key_positives (3-5)
key_concerns (3-5)
forward_guidance
capacity_trends
growth_initiatives (2-3)

Transcript:
{text[:12000]}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        parsed = extract_json_from_response(content)

        if parsed is None:
            return {
                "error": "Groq returned invalid JSON",
                "raw": content
            }

        return parsed

    except Exception as e:
        return {
            "error": "Groq API call failed",
            "details": str(e)
        }

    except json.JSONDecodeError:
        return {"error": "Groq returned invalid JSON after cleanup", "raw": content}
    except Exception as e:

        return {"error": "Groq API call failed", "details": str(e)}
