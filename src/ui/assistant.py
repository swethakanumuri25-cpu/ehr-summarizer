import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_ehr(patient_data, specialty="primary care", mode="clinician"):
    """
    Summarize EHR data into concise clinical notes using LLM.
    """
    prompt = f"""
    You are an intelligent clinical assistant.
    Summarize the following patient's EHR data into concise, accurate clinical notes.
    Specialty: {specialty}
    Mode: {mode} (Clinician = professional tone, Patient = simplified explanation).

    Patient EHR:
    {patient_data}

    Return only the summary.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or gpt-4-turbo / your model
        messages=[{"role": "system", "content": "You are a medical summarization assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response["choices"][0]["message"]["content"]
