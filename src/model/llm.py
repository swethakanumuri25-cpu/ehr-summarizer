import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Add it to the .env file."
    )

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def generate_summary(
    patient_json: dict,
    specialty: str = "primary care",
    mode: str = "clinician"
) -> str:

    if mode == "clinician":
        style = (
            "Write a concise professional clinical documentation summary "
            "for a healthcare clinician."
        )
    else:
        style = (
            "Write a clear patient-friendly explanation using simple "
            "language while preserving important medical information."
        )

    prompt = f"""
You are an AI clinical documentation assistant.

{style}

Clinical specialty: {specialty}

Patient EHR data:
{json.dumps(patient_json, indent=2)}

Instructions:
- Summarize only information present in the supplied EHR.
- Do not invent diagnoses, medications, symptoms, lab results, or treatments.
- Preserve important allergies.
- Mention relevant diagnoses/problems and medications.
- Keep the summary concise and clinically useful.
- Do not provide a new diagnosis or treatment recommendation.
- Return only the summary text.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical documentation summarization assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=500
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Groq returned an empty response.")

    return content.strip()