# EHR Summarizer

An AI-powered Electronic Health Record (EHR) summarization application that converts structured patient information into concise, clinically useful summaries using an LLM, with a FastAPI backend and a Streamlit front end.

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Streamlit
- Groq API (via the OpenAI Python SDK)
- Pydantic
- python-dotenv

## Project Structure

```text
ehr-summarizer/
│
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py            # FastAPI app, POST /summarize
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── load_synthea.py    # Synthea-format EHR loading helpers
│   │
│   ├── model/
│   │   ├── __init__.py
│   │   ├── llm.py             # Groq LLM call for summary generation
│   │   └── pipeline.py        # summarize(): LLM-first, rule-based fallback
│   │
│   └── ui/
│       ├── __init__.py
│       └── app.py             # Streamlit front end
│
├── create_jsons.py
├── requirements.txt
├── .gitignore
└── README.md
```

## How It Works

1. The Streamlit UI (`src/ui/app.py`) collects structured patient JSON, a clinical specialty, and a summary mode (clinician / patient-friendly).
2. It POSTs that payload to the FastAPI backend's `/summarize` endpoint.
3. `pipeline.summarize()` first tries an LLM-generated summary via `llm.py` using a Groq-hosted model.
4. If the LLM call fails for any reason (missing API key, network error, etc.), it falls back to a deterministic, rule-based summary built from the structured fields, and flags this in `issues` so the fallback is never silent.
5. A rule-based validation check compares the generated summary against recorded allergy information and reports potential inconsistencies in `issues`.

## API Endpoint

### POST `/summarize`

Accepts structured patient information and returns a generated clinical summary.

### Example Request

```json
{
  "patient_json": {
    "patient_id": "TEST001",
    "age": 45,
    "gender": "Female",
    "chief_complaint": "Fatigue and occasional dizziness",
    "diagnoses": [
      "Hypertension",
      "Iron deficiency anemia"
    ],
    "medications": [
      "Lisinopril 10 mg daily",
      "Ferrous sulfate 325 mg daily"
    ],
    "allergies": [
      "Penicillin"
    ],
    "vitals": {
      "blood_pressure": "138/88",
      "heart_rate": 78,
      "temperature": "98.6 F"
    },
    "lab_results": {
      "hemoglobin": "10.8 g/dL",
      "ferritin": "12 ng/mL"
    },
    "assessment": "Fatigue likely associated with iron deficiency. Blood pressure remains mildly elevated."
  },
  "specialty": "primary care",
  "mode": "clinician"
}
```

### Example Response

```json
{
  "summary": "45-year-old female presenting with fatigue and occasional dizziness. History notable for hypertension and iron deficiency anemia, currently managed with lisinopril and ferrous sulfate. Patient has a documented penicillin allergy.",
  "citations": [],
  "timeline": [],
  "issues": []
}
```

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/swethakanumuri25-cpu/ehr-summarizer.git
cd ehr-summarizer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**macOS/Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

**Never commit `.env` or API keys to GitHub.**

### 6. Start the API

```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8081
```

Swagger UI is then available at:

```text
http://localhost:8081/docs
```

### 7. Start the Streamlit UI

In a separate terminal (with the venv activated):

```bash
streamlit run src/ui/app.py
```

This opens the app at `http://localhost:8501`. The UI expects the backend to be running on `localhost:8081`.

## Safety Considerations

This project is intended for demonstration and development purposes, not clinical use.

The summarization system is instructed to:

- Avoid inventing clinical information
- Preserve relevant patient information
- Preserve important allergies
- Mention relevant diagnoses and medications
- Avoid generating new diagnoses
- Avoid providing new treatment recommendations

The generated output should not be treated as a substitute for professional medical judgment.

## Future Improvements

- Add authentication and authorization
- Add persistent EHR storage
- Improve citation and source tracking
- Add evaluation metrics for summary quality
- Add automated testing
- Add production deployment
- Improve clinical information extraction
- Add support for additional EHR formats

## Author

**Swetha Kanumuri**

MS in Data Science, University of North Texas