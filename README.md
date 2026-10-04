# 🎯 HireLens AI — Role-Based AI Recruitment Platform

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**HireLens AI** is an intelligent, explainable, role-based recruitment platform built to streamline the hiring process between recruiters and job seekers. Featuring requirement-aware skill matching, TF-IDF cosine similarity scoring, deterministic claim verification, resume quality assessment, recruiter decision intelligence ("Why This Candidate?"), and privacy-preserving candidate feedback.

---

## 📌 Problem Statement
Traditional hiring workflows suffer from slow resume screening, manual qualification verification, and unexplainable black-box applicant scoring. Recruiters spend dozens of hours manually reading PDF resumes, while candidates receive little to no feedback on why their profile was accepted or rejected. 

**HireLens AI** solves this by delivering an automated, explainable, and secure recruitment platform that:
- Instantly parses PDF resumes and extracts technical skills.
- Ranks candidates with requirement-aware scoring (Required vs. Preferred vs. Bonus skills).
- Flags potential timeline inconsistencies and unsupported claims without accusations.
- Computes resume quality indicators to warn recruiters of weak extractions.
- Empowers recruiters with deterministic "Why This Candidate?" decision support.
- Delivers actionable skill-gap feedback directly to candidates without exposing recruiter notes or competitor data.

---

## ✨ Key Features

### 👤 Candidate Features
- **Secure Registration & Authentication**: Role-based signup with salted PBKDF2-SHA256 password hashing.
- **Job Browsing**: Explore active job postings with clear breakdowns of Required, Preferred, and Bonus skills.
- **PDF Resume Upload**: Apply to positions by uploading standard PDF resumes.
- **Resume Quality Indicator**: Instant feedback on whether the resume was parsed successfully (`GOOD`, `LIMITED`, or `POOR`), alerting candidates to scanned or text-poor documents.
- **Application Tracking & Privacy-Safe Feedback**: Candidates see their overall match score, matched skills, missing required skills, missing preferred skills, and skills to strengthen. Recruiter notes, verification flags, and other applicants' data are strictly withheld.
- **Duplicate Application Prevention**: Guards against duplicate applications for the same job posting.

### 💼 Employer / Recruiter Features
- **Requirement-Aware Job Creation**: Specify jobs with categorized skills:
  - **Required Skills** (Critical for role eligibility)
  - **Preferred Skills** (Strong differentiators)
  - **Bonus Skills** (Nice-to-have additions)
  *(All skill tiers are optional; existing legacy jobs continue to work seamlessly).*
- **Requirement-Aware Candidate Ranking**: Automatically ranks applicants using the hybrid deterministic formula.
- **"Why This Candidate?" Decision Intelligence**:
  - Overall Match Score & Critical Skill Coverage.
  - Recruiter Recommendation: `STRONG MATCH`, `GOOD MATCH`, `PARTIAL MATCH`, or `WEAK MATCH`.
  - Top Strengths & Critical Gaps.
  - Verification Flags summary.
  *(recruiter decision support only — does not make automated hire/reject decisions).*
- **Deterministic Claim Verification**:
  - Identifies unsupported skill claims (skills in skill list without project/work context).
  - Flags overlapping employment periods.
  - Flags timeline inconsistencies (e.g., claimed years exceeding employment date spans).
  - Human-review oriented: uses non-accusatory terminology such as *"Verification Recommended"* and *"Potential inconsistency detected"*.
- **Resume Quality Indicator**: Badges (`GOOD`, `LIMITED`, `POOR`) alerting recruiters if match scores may be skewed due to scanned/low-text PDFs.
- **Search & Filtering**: Search applicants by name/email and filter by status, minimum match score, or specific skill tags.
- **Applicant Status Management**: Shortlist or reject candidates with real-time candidate dashboard synchronization.
- **Strict Ownership Isolation**: Employers can only access their own jobs, applicants, and match analytics.

---

## 🏗️ Architecture & Project Structure

```
algoxilla/
│
├── app.py                      # Main Streamlit application entrypoint & role router
├── requirements.txt            # Python package dependencies
├── README.md                   # Comprehensive system documentation
├── .gitignore                  # Git ignore rules for DB, cache, and uploaded files
│
├── database/
│   ├── database.py             # SQLite connection management & safe schema migrations
│   └── hirelens.db             # Local SQLite database
│
├── auth/
│   ├── auth.py                 # User registration, login, and salted PBKDF2 password hashing
│   └── roles.py                # Streamlit session state and role helper utilities
│
├── candidate/
│   └── candidate_dashboard.py  # Candidate dashboard UI (Job browsing, Applying, Privacy-safe feedback)
│
├── employer/
│   └── employer_dashboard.py   # Employer dashboard UI (Job posting, Ranking, "Why This Candidate?", Filters)
│
├── ai/
│   ├── resume_parser.py        # PyMuPDF (fitz) text extraction engine
│   ├── text_processor.py       # Text normalization & boundary-aware regex skill extraction
│   ├── matcher.py              # Scikit-Learn TF-IDF Vectorizer & Cosine Similarity
│   ├── scorer.py               # Requirement-aware scoring engine (40% TF-IDF + 40% Req + 15% Pref + 5% Bonus)
│   ├── explainer.py            # Rule-based recruiter & candidate match breakdown generator
│   ├── verifier.py             # Deterministic claim verification engine (evidence, timeline, overlap checks)
│   ├── quality.py              # Resume extraction quality indicator (GOOD, LIMITED, POOR)
│   └── recommender.py          # Recruiter decision intelligence ("Why This Candidate?" support)
│
├── jobs/
│   └── job_manager.py          # Job & Application database CRUD operations & security enforcement
│
├── utils/
│   ├── constants.py            # Predefined technical skill taxonomy
│   └── helpers.py              # Safe file upload handling & relative path utilities
│
└── uploads/
    └── resumes/                # Uploaded candidate PDF resumes
```

---

## 🛠️ Tech Stack
- **Frontend / UI**: [Streamlit](https://streamlit.io) (v1.30+)
- **Backend Core**: Python 3.10+
- **Database**: SQLite3 (with `PRAGMA foreign_keys = ON;` and safe column migrations)
- **PDF Extraction**: [PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/)
- **Machine Learning & NLP**: [scikit-learn](https://scikit-learn.org/) (`TfidfVectorizer`, `cosine_similarity`)
- **Password Security**: Standard Library `hashlib` (PBKDF2-HMAC-SHA256 with 100,000 iterations and random 16-byte salt)
- **No Heavy Frameworks**: Zero external REST APIs, zero LLM token costs, zero vector databases, zero Docker/Node/Redis requirements.

---

## 🧠 AI & Match Scoring Pipeline

```
┌─────────────────┐       ┌──────────────────────┐
│  Candidate PDF  │ ────> │  PyMuPDF Text Parser │
└─────────────────┘       └──────────┬───────────┘
                                     │ Extracted Text
                                     ▼
                          ┌──────────────────────┐
                          │   Text Normalizer    │
                          └──────────┬───────────┘
                                     │ Cleaned Text
                                     ▼
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ Skill Taxonomy  │ ────> │ Regex Skill Detector │ ────> │   Quality Analyzer   │
└─────────────────┘       └──────────┬───────────┘       │ (GOOD, LIMITED, POOR)│
                                     │ Detected Skills   └──────────────────────┘
                                     ▼
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ Job Description │ ────> │ TF-IDF + Cosine Sim  │ ────> │ Claim Verification   │
│ & Requirements  │       └──────────┬───────────┘       │ (Timeline, Overlaps, │
└─────────────────┘                  │ TF-IDF Score      │  Unsupported claims) │
                                     ▼                   └──────────────────────┘
                          ┌──────────────────────┐                   │
                          │ Requirement-Aware    │                   ▼
                          │ Scoring Engine       │       ┌──────────────────────┐
                          │ (40/40/15/5 Formula) │ ────> │ "Why This Candidate?"│
                          └──────────┬───────────┘       │  Decision Recommender│
                                     │ Final Score       └──────────────────────┘
                                     ▼
                          ┌──────────────────────┐
                          │ Explainable Matching │
                          │ Recruiter & Candidate│
                          └──────────────────────┘
```

### 1. Resume Parsing
PyMuPDF (`pymupdf`) extracts raw text from PDF uploads, handling multi-column formats and multi-page layouts cleanly with defensive fallback handling.

### 2. Skill Extraction
Uses boundary-aware regular expressions against a taxonomy of 100+ technical skills. Prevents false positive substring matches (e.g., distinguishing `C++` from `C`, or `Java` from `JavaScript`).

### 3. TF-IDF & Cosine Similarity
Resume text and job description are transformed via `scikit-learn`'s `TfidfVectorizer` (sublinear TF scaling, English stopwords removed) to measure holistic content and domain alignment.

### 4. Deterministic Requirement-Aware Scoring Formula
When jobs specify categorized skills, the final score (0–100, rounded to 1 decimal place) is computed as:

$$\text{Final Score} = 40\% \times \text{TF-IDF Similarity} + 40\% \times \text{Required Coverage} + 15\% \times \text{Preferred Coverage} + 5\% \times \text{Bonus Coverage}$$

Where:
- $\text{Required Coverage} = \frac{\text{Matched Required Skills}}{\text{Total Required Skills}}$
- $\text{Preferred Coverage} = \frac{\text{Matched Preferred Skills}}{\text{Total Preferred Skills}}$
- $\text{Bonus Coverage} = \frac{\text{Matched Bonus Skills}}{\text{Total Bonus Skills}}$

*Note: If any skill category has zero skills configured, its weight is gracefully redistributed to avoid division-by-zero. For legacy jobs without skill categories, the platform retains backward-compatible scoring (70% skill overlap + 30% TF-IDF).*

---

## 🔍 Claim Verification Engine

HireLens AI includes lightweight, deterministic claim verification to support recruiter due diligence:

1. **Unsupported Skill Claims**: Flags skills listed under a "Skills" summary that lack corroborating context in Experience or Projects sections.
2. **Employment Timeline Overlaps**: Flags concurrent full-time employment date ranges.
3. **Experience Duration Inconsistencies**: Flags resumes where stated total experience contradicts the computed span of employment history.
4. **Education/Experience Timeline Mismatches**: Flags obvious sequence anomalies.

### ⚠️ Important Verification Disclaimer
> **Recruiter Assistance Only**: Claim verification checks are strictly deterministic heuristics intended to highlight areas for recruiter follow-up. They do **NOT** determine whether a candidate is truthful or fraudulent. The platform strictly prohibits accusatory language (e.g., "fake candidate", "lying", or "fraud") and instead provides objective flags labeled *"Verification Recommended"* and *"Potential inconsistency detected"*.

---

## 📊 Resume Quality Indicator

To safeguard against misleading scores from scanned or malformed PDFs:
- **`GOOD`**: Comprehensive text extraction (>100 words, skills detected).
- **`LIMITED`**: Moderate text length (30–99 words), potential incomplete extraction.
- **`POOR`**: Minimal or empty text (<30 words, zero skills), likely scanned image PDF.
  - Displays notice: *"Limited resume text extracted. Match score may be unreliable."*
  - Candidates are still permitted to apply without arbitrary blocking.

---

## 💡 Recruiter Decision Intelligence ("Why This Candidate?")

In the Employer dashboard, recruiters receive structured, deterministic decision intelligence for each applicant:
- **Overall Match Score** & **Critical Skill Coverage**.
- **Recommendation Tiers**:
  - `STRONG MATCH`: High overall score (≥70%) with 100% Critical Skill Coverage.
  - `GOOD MATCH`: Strong overall score (≥60%) with ≥66% Critical Skill Coverage.
  - `PARTIAL MATCH`: Moderate score (≥40%) or partial critical skill coverage.
  - `WEAK MATCH`: Low score (<40%) or missing all critical skills.
- **Top Strengths**: Verified required/preferred skills and strong text alignment.
- **Critical Gaps**: Missing required skills that need immediate evaluation.
- **Verification Flags**: Summary of timeline or evidence flags requiring interview follow-up.

---

## 🗄️ Database Schema & Migrations

The database (`database/hirelens.db`) uses SQLite with automatic safe column migrations:

### `users` Table
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL
- `email`: TEXT UNIQUE NOT NULL
- `password`: TEXT NOT NULL *(PBKDF2-HMAC-SHA256 salted hash)*
- `role`: TEXT NOT NULL CHECK(role IN ('candidate', 'employer'))
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### `jobs` Table
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `employer_id`: INTEGER NOT NULL (FOREIGN KEY -> `users.id`)
- `title`: TEXT NOT NULL
- `company`: TEXT NOT NULL
- `description`: TEXT NOT NULL
- `location`: TEXT
- `required_skills`: TEXT DEFAULT '' *(comma-separated, migrated safely)*
- `preferred_skills`: TEXT DEFAULT '' *(comma-separated, migrated safely)*
- `bonus_skills`: TEXT DEFAULT '' *(comma-separated, migrated safely)*
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### `applications` Table
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `candidate_id`: INTEGER NOT NULL (FOREIGN KEY -> `users.id`)
- `job_id`: INTEGER NOT NULL (FOREIGN KEY -> `jobs.id`)
- `resume_path`: TEXT
- `match_score`: REAL DEFAULT 0
- `status`: TEXT DEFAULT 'Applied'
- `applied_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 🔒 Security & Privacy Architecture

- **Cryptographic Password Storage**: Passwords are salted using `os.urandom(16)` and hashed via `hashlib.pbkdf2_hmac` (SHA-256, 100k rounds). Plaintext passwords are never saved.
- **Cross-Employer Isolation**: Employers cannot access job postings, applicants, or match analyses belonging to other employers.
- **Cross-Candidate Isolation**: Candidates cannot view submissions, resumes, or scores of other applicants.
- **Recruiter Data Privacy**: Candidates never see verification flags, recruiter recommendation badges, or employer notes. Candidate feedback is limited strictly to their own match score and skill-gap suggestions.
- **SQL Injection Prevention**: All queries use parameterized SQL bindings (`?`).

---

## 🧪 Comprehensive Automated Testing

Run the full end-to-end automated test suite:

```bash
python test_final.py
```

The test suite validates:
- **TEST A**: Strong Candidate (Required 3/3, Preferred 2/2, Bonus 1/1 → High score & `GOOD/STRONG MATCH`).
- **TEST B**: Partial Candidate (Required 2/3, Preferred 1/2, Bonus 0/1 → Moderate score).
- **TEST C**: Weak Candidate (Required 0/3, Preferred 0/2, Bonus 0/1 → Low score & `WEAK MATCH`).
- **TEST D**: Priority Ordering (Missing Required skill penalizes score more than missing Preferred, which penalizes more than Bonus).
- **TEST E**: TF-IDF & Cosine Similarity validation.
- **TEST F**: Empty skills handling & zero division avoidance across legacy jobs.
- **TEST G**: Resume Quality Indicator on good, short, empty, and corrupted PDFs.
- **TEST H**: Deterministic Claim Verification (timeline overlaps, unsupported skills, experience conflicts, non-accusatory language).
- **TEST I**: Security & Ownership Isolation (cross-employer and cross-candidate data leakage prevention).
- **TEST J**: Full 15-step End-to-End Regression flow (Registration → Application → Scoring → Ranking → Feedback → Status Sync).
- **DB Integrity**: Table row persistence, foreign keys, and column migration validation.

---

## 🚀 Setup & Local Execution

### Prerequisites
- Python 3.10 or higher
- `pip`

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/algoxilla.git
   cd algoxilla
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application**:
   ```bash
   streamlit run app.py
   ```

5. Open your browser at `http://localhost:8501`.

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

1. Push your repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select your repository, branch (`main`), and set the main file path to `app.py`.
4. Deploy! The SQLite database and file upload paths will initialize automatically.

---

## 📝 Limitations & Future Improvements

- **Scanned Document OCR**: Image-only PDF resumes without selectable text trigger the `POOR` quality indicator; future versions could integrate lightweight Tesseract OCR.
- **Synonym & Semantic Skill Taxonomies**: Technical skill matching currently relies on normalized regex; future iterations could include word embeddings or ontology mappings (e.g., mapping `k8s` to `Kubernetes`).
- **Interview Scheduling**: Future versions could integrate calendar coordination for shortlisted candidates.

---

## 📄 License
This project is licensed under the MIT License.
