"""from fastapi import FastAPI
from pydantic import BaseModel
from src.model.pipeline import summarize

#print(">>> main.py loaded successfully <<<")#


app = FastAPI(title="EHR Summarizer API")

class SummarizeRequest(BaseModel):
    patient_json: dict
    specialty: str = "primary care"
    mode: str = "clinician"

@app.post("/summarize")
def summarize_endpoint(req: SummarizeRequest):
    return summarize(req.patient_json, req.specialty, req.mode)"""

"""from fastapi import FastAPI
from pydantic import BaseModel

print(">>> main.py started <<<")

try:
    from src.model.pipeline import summarize
    print(">>> pipeline import successful <<<")
except Exception as e:
    print(">>> pipeline import failed:", e)

app = FastAPI(title="EHR Summarizer API")

class SummarizeRequest(BaseModel):
    patient_json: dict
    specialty: str = "primary care"
    mode: str = "clinician"

@app.post("/summarize")
def summarize_endpoint(req: SummarizeRequest):
    return {"summary": "Test OK"}"""


from fastapi import FastAPI
from pydantic import BaseModel

print(">>> main.py started <<<")

try:
    from src.model.pipeline import summarize
    print(">>> pipeline import successful <<<")
except Exception as e:
    print(">>> pipeline import failed:", e)


from fastapi import FastAPI
from pydantic import BaseModel
from src.model.pipeline import summarize  # Make sure your file is named pipeline.py (not Pipeline.py)

# Confirm module loading
print(">>> main.py started <<<")

try:
    from src.model.pipeline import summarize
    print(">>> pipeline import successful <<<")
except Exception as e:
    print(">>> pipeline import failed:", e)

# Create FastAPI app instance
app = FastAPI(title="EHR Summarizer API")

# Define request model
class SummarizeRequest(BaseModel):
    patient_json: dict
    specialty: str = "primary care"
    mode: str = "clinician"

# Define API endpoint
@app.post("/summarize")
def summarize_endpoint(req: SummarizeRequest):
    return summarize(req.patient_json, req.specialty, req.mode)

"""from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Connect to Groq API instead of OpenAI
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI(title="EHR Summarizer API")

# Define request schema
class SummarizeRequest(BaseModel):
    patient_json: dict
    specialty: str = "primary care"
    mode: str = "clinician"

@app.post("/summarize")
def summarize_endpoint(req: SummarizeRequest):
    ummarize EHR data using Groq LLM (Llama3).
    prompt = f 
    You are an AI clinical documentation assistant.
    Summarize the following patient's EHR data concisely and accurately.

    Specialty: {req.specialty}
    Mode: {req.mode}
      - Clinician → professional, concise medical summary.
      - Patient → simplified, easy-to-understand explanation.

    EHR Data:
    {req.patient_json}

    Return only the summary. 

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",   # Groq-supported model
            messages=[
                {"role": "system", "content": "You are a clinical summarization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400
        )

        summary = response.choices[0].message.content.strip()
        return {"summary": summary}

    except Exception as e:
        return {"error": str(e)}"""