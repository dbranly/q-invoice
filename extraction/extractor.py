import os
import json
import re
from dotenv import load_dotenv
from jsonschema import validate
from openai import OpenAI

from ocr.paddle_ocr import run_ocr
from extraction.schema import DOCUMENT_SCHEMA
from extraction.normalizer import normalize_document

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM output")
    return json.loads(match.group())


def extract_document(image_path: str) -> dict:
    ocr_text = run_ocr(image_path)

    prompt = f"""
You are an expert document parser.

OCR TEXT:
{ocr_text}

Return ONLY valid JSON.
Use null when unknown.
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    raw_text = response.output_text or ""
    raw_json = extract_json(raw_text)

    normalized = normalize_document(raw_json)
    validate(instance=normalized, schema=DOCUMENT_SCHEMA)

    return normalized
