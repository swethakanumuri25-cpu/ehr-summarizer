import streamlit as st
import json
import requests


# ============================================================
# PAGE CONFIGURATION
# ============================================================

STETHOSCOPE = "\U0001FA7A"

st.set_page_config(
    page_title="EHR AI Assistant",
    page_icon=STETHOSCOPE,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HTML RENDER HELPER
# ============================================================
# st.markdown(..., unsafe_allow_html=True) still runs content
# through the Markdown parser first. Markdown treats any line
# indented 4+ spaces as a code block, and because these HTML
# snippets live inside indented Python code, that's exactly what
# was happening -- the tags were being printed as literal text
# instead of being rendered as HTML. Stripping each line's
# leading whitespace before handing it to st.markdown fixes it.

def render_html(content: str) -> None:
    dedented = "\n".join(line.lstrip() for line in content.strip("\n").split("\n"))
    st.markdown(dedented, unsafe_allow_html=True)


# ============================================================
# CUSTOM CSS
# ============================================================

render_html(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #f5f7fb;
    }

    .main .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                     Roboto, Helvetica, Arial, sans-serif;
    }


    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    .sidebar-brand {
        padding: 10px 4px 22px 4px;
    }

    .sidebar-brand-title {
        font-size: 1.35rem;
        font-weight: 750;
        color: #172033;
        display: flex;
        align-items: center;
        gap: 9px;
    }

    .sidebar-brand-icon {
        font-size: 1.45rem;
    }

    .sidebar-brand-text {
        color: #687386;
        font-size: 0.88rem;
        line-height: 1.55;
        margin-top: 8px;
    }

    .sidebar-divider {
        height: 1px;
        background: #e5e7eb;
        margin: 18px 0 25px 0;
    }

    .sidebar-section-title {
        color: #3b4352;
        font-size: 0.78rem;
        font-weight: 750;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .sidebar-about {
        color: #737d8f;
        font-size: 0.82rem;
        line-height: 1.6;
    }


    /* ---------- HEADER ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #173f68 0%,
            #176f83 55%,
            #15938d 100%
        );

        border-radius: 22px;
        padding: 38px 42px;
        color: white;
        box-shadow: 0 12px 30px rgba(23, 63, 104, 0.16);
        margin-bottom: 24px;
    }

    .hero-icon {
        font-size: 2.8rem;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 780;
        line-height: 1.15;
        margin-bottom: 10px;
    }

    .hero-description {
        font-size: 1rem;
        line-height: 1.6;
        opacity: 0.92;
        max-width: 700px;
    }

    .hero-badge {
        display: inline-block;
        margin-top: 18px;
        padding: 7px 13px;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.25);
        font-size: 0.78rem;
        font-weight: 650;
    }


    /* ---------- STATUS CARD ---------- */

    .status-card {
        background: white;
        border: 1px solid #e4e8ef;
        border-radius: 16px;
        padding: 17px 20px;
        margin-bottom: 26px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .status-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        background: #22c55e;
        box-shadow: 0 0 0 4px #dcfce7;
    }

    .status-dot-offline {
        background: #ef4444;
        box-shadow: 0 0 0 4px #fee2e2;
    }

    .status-title {
        color: #172033;
        font-weight: 700;
        font-size: 0.95rem;
    }

    .status-subtitle {
        color: #7a8495;
        font-size: 0.78rem;
        margin-top: 2px;
    }


    /* ---------- SECTION TITLE ---------- */

    .section-title {
        color: #172033;
        font-size: 1.25rem;
        font-weight: 750;
        margin: 24px 0 12px 0;
    }

    .section-description {
        color: #6b7485;
        font-size: 0.9rem;
        margin-bottom: 15px;
    }


    /* ---------- INFO CARDS ---------- */

    .info-card {
        background: white;
        border: 1px solid #e4e8ef;
        border-radius: 15px;
        padding: 18px;
        min-height: 95px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.035);
    }

    .info-label {
        color: #7a8495;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
    }

    .info-value {
        color: #172033;
        font-size: 1rem;
        font-weight: 650;
    }


    /* ---------- INPUT CARD ---------- */

    .input-card {
        background: white;
        border: 1px solid #e4e8ef;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
        margin-top: 18px;
    }


    /* ---------- BUTTON ---------- */

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        min-height: 48px;
        font-weight: 700;
        font-size: 0.95rem;
        border: none;
        background: #176f83;
        color: white;
    }

    div.stButton > button:hover {
        background: #145f70;
        color: white;
    }


    /* ---------- SUMMARY ---------- */

    .summary-card {
        background: white;
        border: 1px solid #dfe5ec;
        border-radius: 18px;
        padding: 25px;
        margin-top: 18px;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.045);
    }

    .summary-heading {
        color: #172033;
        font-size: 1.15rem;
        font-weight: 750;
        margin-bottom: 15px;
    }

    .summary-text {
        color: #394355;
        font-size: 0.95rem;
        line-height: 1.7;
        white-space: pre-wrap;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #8a93a3;
        font-size: 0.78rem;
        padding: 35px 0 10px 0;
    }

    </style>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        f"""
        <div class="sidebar-brand">

            <div class="sidebar-brand-title">
                <span class="sidebar-brand-icon">{STETHOSCOPE}</span>
                <span>EHR AI Assistant</span>
            </div>

            <div class="sidebar-brand-text">
                AI-powered clinical documentation and
                patient information summarization.
            </div>

        </div>
        """
    )

    render_html('<div class="sidebar-divider"></div>')

    render_html('<div class="sidebar-section-title">Summary Mode</div>')

    mode = st.radio(
        "Summary mode",
        ["Clinician", "Patient-friendly"],
        label_visibility="collapsed"
    )

    render_html('<br>')

    render_html('<div class="sidebar-section-title">Clinical Specialty</div>')

    specialty = st.selectbox(
        "Clinical specialty",
        [
            "primary care",
            "cardiology",
            "pediatrics",
            "oncology",
            "ED"
        ],
        label_visibility="collapsed"
    )

    render_html('<div class="sidebar-divider"></div>')

    render_html(
        """
        <div class="sidebar-section-title">About</div>

        <div class="sidebar-about">
            This application transforms structured
            Electronic Health Record data into concise
            documentation summaries.

            <br><br>

            The application communicates with a local
            FastAPI backend running on port 8081.
        </div>
        """
    )


# ============================================================
# MAIN HEADER
# ============================================================

render_html(
    f"""
    <div class="hero">

        <div class="hero-icon">{STETHOSCOPE}</div>

        <div class="hero-title">
            EHR AI Assistant
        </div>

        <div class="hero-description">
            AI-powered clinical documentation and
            patient information summarization.
        </div>

        <div class="hero-badge">
            Clinical Documentation Support
        </div>

    </div>
    """
)


# ============================================================
# BACKEND STATUS
# ============================================================

backend_url = "http://localhost:8081"

backend_online = False

try:
    requests.get(
        f"{backend_url}/docs",
        timeout=2
    )
    backend_online = True
except Exception:
    backend_online = False


if backend_online:

    render_html(
        """
        <div class="status-card">

            <div class="status-left">

                <span class="status-dot"></span>

                <div>
                    <div class="status-title">
                        EHR AI Assistant
                    </div>

                    <div class="status-subtitle">
                        Backend connected &middot; FastAPI &middot; localhost:8081
                    </div>
                </div>

            </div>

        </div>
        """
    )

else:

    render_html(
        """
        <div class="status-card">

            <div class="status-left">

                <span class="status-dot status-dot-offline"></span>

                <div>
                    <div class="status-title">
                        EHR AI Assistant
                    </div>

                    <div class="status-subtitle">
                        Backend offline &middot; Start FastAPI on localhost:8081
                    </div>
                </div>

            </div>

        </div>
        """
    )


# ============================================================
# PATIENT INFORMATION
# ============================================================

render_html('<div class="section-title">Patient Information</div>')

col1, col2 = st.columns(2)

with col1:
    render_html(
        """
        <div class="info-card">

            <div class="info-label">
                Summary Mode
            </div>

            <div class="info-value">
                {mode}
            </div>

        </div>
        """.replace("{mode}", mode)
    )

with col2:
    render_html(
        """
        <div class="info-card">

            <div class="info-label">
                Clinical Specialty
            </div>

            <div class="info-value">
                {specialty}
            </div>

        </div>
        """.replace("{specialty}", specialty.title())
    )


# ============================================================
# PATIENT JSON INPUT
# ============================================================

render_html('<div class="section-title">Patient Record</div>')

render_html(
    """
    <div class="section-description">
        Paste structured patient JSON below to generate
        a concise clinical summary.
    </div>
    """
)


example_json = """{
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
}"""


with st.container():

    raw = st.text_area(
        "Patient JSON",
        value=example_json,
        height=350,
        label_visibility="collapsed",
        placeholder="Paste patient JSON here..."
    )


# ============================================================
# SUMMARIZE BUTTON
# ============================================================

if st.button("Generate Clinical Summary"):

    # -----------------------------------------
    # Validate JSON
    # -----------------------------------------

    try:
        patient_data = json.loads(raw)

    except json.JSONDecodeError as e:

        st.error(
            f"Invalid JSON. Please check the patient record format.\n\n{e}"
        )

        st.stop()


    # -----------------------------------------
    # Create backend payload
    # -----------------------------------------

    payload = {
        "patient_json": patient_data,
        "specialty": specialty,
        "mode": "patient" if mode == "Patient-friendly" else "clinician"
    }


    # -----------------------------------------
    # Backend request
    # -----------------------------------------

    with st.spinner("Generating clinical summary..."):

        try:

            response = requests.post(
                f"{backend_url}/summarize",
                json=payload,
                timeout=120
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the FastAPI backend. "
                "Please make sure the backend is running on port 8081."
            )

            st.stop()

        except requests.exceptions.Timeout:

            st.error(
                "The backend took too long to respond. "
                "Please check the FastAPI terminal."
            )

            st.stop()

        except Exception as e:

            st.error(f"Request failed: {str(e)}")

            st.stop()


    # -----------------------------------------
    # Process response
    # -----------------------------------------

    if response.status_code != 200:

        st.error(
            f"Backend returned HTTP {response.status_code}"
        )

        with st.expander("Backend response"):

            st.code(
                response.text,
                language="text"
            )

        st.stop()


    try:

        result = response.json()

    except ValueError:

        st.error("Backend returned an invalid JSON response.")

        with st.expander("Raw backend response"):

            st.code(
                response.text,
                language="text"
            )

        st.stop()


    # -----------------------------------------
    # Error from backend
    # -----------------------------------------

    if result.get("error"):

        st.error(result["error"])


    # -----------------------------------------
    # Display summary
    # -----------------------------------------

    summary = result.get("summary")

    if summary:

        render_html(
            """
            <div class="summary-card">

                <div class="summary-heading">
                    Clinical Summary
                </div>

            </div>
            """
        )

        render_html(
            """
            <div class="summary-card">

                <div class="summary-text">
                    {summary}
                </div>

            </div>
            """.replace("{summary}", summary)
        )


    else:

        st.warning(
            "The backend responded, but no summary was returned."
        )


    # -----------------------------------------
    # Issues / warnings
    # -----------------------------------------

    if result.get("issues"):

        render_html('<div class="section-title">Clinical Notes</div>')

        for issue in result["issues"]:

            st.warning(issue)


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">
        EHR AI Assistant &middot; Clinical Documentation Support
    </div>
    """
)