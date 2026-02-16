# Job Hunter AI – Automated Resume and Cover Letter Generation

[![CI Pipeline](https://github.com/YOUR_USERNAME/job-hunter-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/job-hunter-ai/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Job Hunter AI is an end-to-end automation system designed to streamline the job application process for Data Engineering roles.
It automates job ingestion, filtering, scoring, and the generation of tailored resumes and cover letters using LaTeX and LLMs (Groq).

The goal of the system is to eliminate repetitive manual application tasks and to produce high-quality, role-specific application documents.

---

## 1. Overview

The system performs the following tasks:

1. Automatically fetch job listings from external APIs (currently Adzuna).
2. Filter and classify job posts using a deterministic rule engine.
3. Score each job using a hybrid method (deterministic logic + LLM evaluation).
4. Generate structured, high-detail JSON describing:
   - Tailored CV content  
   - Tailored cover letter content  
   - Selected technical bullets  
   - Selected project bullets  
5. Render LaTeX templates into `.tex` files (one-page resume and cover letter).
6. Optionally upload outputs to Google Drive.
7. Track job pipeline state using Google Sheets.
8. Prepare for orchestration with n8n.

The project is modular and designed for extension to multiple job sources, LLM providers, and resume templates.

---

## 2. Architecture

job-hunter-ai/
├── src/
│ ├── job_hunter_ai/
│ │ ├── llm/
│ │ │ └── enrich.py
│ │ ├── latex/
│ │ │ └── render_template.py
│ │ ├── scoring/
│ │ │ └── scoring.py
│ │ ├── ingestion/
│ │ │ └── ingest_adzuna.py
│ │ └── utils/
│ │ └── text_cleaning.py
├── prompts/
│ ├── cv_master_prompt.txt
│ ├── cv_one_page_prompt.txt
│ ├── cover_letter_prompt.txt
├── profile/
│ ├── profile.yml
│ ├── experiences.md
│ └── projects.md
├── templates/
│ ├── cv_template.tex
│ └── cover_template.tex
├── scripts/
│ ├── test_llm_generation.py
│ ├── ingest_jobs.py
│ ├── scoring_test.py
│ └── generate_docs_for_job.py
└── generated_jobs/


---

## 3. Job Ingestion

### Source  
Currently implemented: **Adzuna API**  
Planned: France Travail, Jooble, Indeed (if supported), custom scrapers.

### Processing Steps

1. Fetch jobs from API.
2. Normalize fields (title, company, city, contract, description).
3. Compute `job_id` using SHA-1 to avoid duplicates.
4. Filter jobs using deterministic rules:
   - Exclude internships, alternance, apprenticeships.
   - Exclude senior/executive postings.
   - Extract location using custom regex patterns.
5. Write job entries to Google Sheets with columns:

job_id | source | title | company | city | country | url |
description | created_at | status


Statuses:
- `NEW`: newly ingested
- `SKIPPED`: excluded by rules
- `LLM_READY`: ready for scoring and CV generation

---

## 4. Deterministic Scoring System

Implemented in `scoring/scoring.py`.

Evaluates:
- Required vs. optional keyword matches
- Cloud & data engineering technologies
- SQL, Python, PySpark, Airflow, Kafka, Terraform
- Minimum required experience
- Role title similarity
- Disqualifying signals

Produces a score from **0 to 100**.

---

## 5. Hybrid LLM Scoring

The hybrid score combines deterministic and LLM perspectives.

### Inputs to LLM:
- Job description
- Your profile (`profile.yml`)
- Experiences (`experiences.md`)
- Projects (`projects.md`)

### Outputs:
- `summary`
- `experience` (tailored bullets per job)
- `projects` (selected high-relevance projects)
- `skills_focus`
- `fit_reasoning`
- `llm_score` (0–100)

### Final Score


final_score = 0.65 * deterministic_score + 0.35 * llm_score


---

## 6. Knowledge Base

Stored under `/profile/`.

### profile.yml  
Contains structured data:
- Identity  
- Location  
- Years of experience  
- Seniority  
- Technical stack  
- Architecture experience  
- Domain exposure  
- Strengths  

### experiences.md  
Rich descriptions of:
- Socotec  
- Leyton  
- Bourse de Casablanca  
- Wafa Gestion  

### projects.md  
Projects with:
- One-liner  
- Technical bullets  
- Stack used  
- Practical value  

This knowledge base ensures:
- Consistency
- No hallucinated content
- High realism
- Strong project relevance

---

## 7. LLM Prompts

### cv_master_prompt.txt  
Produces a rich, multi-section JSON containing:
- Detailed bullets per experience
- Selected projects with one-liners
- Skills to emphasize
- Professional summary

### cv_one_page_prompt.txt  
Compresses master content into:
- A one-page CV  
- Limited bullet count  
- Role alignment  
- High-density technical impact  

### cover_letter_prompt.txt  
Generates:
- Intro paragraph referencing company  
- 3–4 technical paragraphs  
- Closing paragraph  
- Professional tone  

---

## 8. LaTeX Rendering

The system:
1. Loads a `.tex` template (resume or cover letter).
2. Fills placeholders with LLM outputs.
3. Writes a full `.tex` file to:

generated_jobs/<job_id>/


PDF compilation is intentionally not automated because of inconsistent LaTeX engines on Windows.  
Instead, users upload `.tex` to Overleaf or compile with MiKTeX manually.

---

## 9. n8n Integration (Planned)

The pipeline will be orchestrated via n8n:

[ Cron Trigger ]
↓
[ Call ingest_jobs.py ]
↓
[ Call scoring + LLM generation ]
↓
[ Generate CV + Cover Letter ]
↓
[ Upload to Google Drive ]
↓
[ Update Google Sheets ]
↓
[ Notify user ]


Future additions:
- Auto-apply for supported APIs
- Retry logic
- Weekly job summary email
- Telegram/Discord notifications

---

## 10. Requirements

Python:
python >= 3.10
groq
requests
gspread
google-auth
PyYAML
python-dotenv
