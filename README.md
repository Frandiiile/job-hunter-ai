# Job Hunter AI

[![CI Pipeline](https://github.com/Frandiiile/job-hunter-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Frandiiile/job-hunter-ai/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Automated resume and cover letter generation system for Data Engineering roles using AI and LaTeX

Job Hunter AI is an end-to-end automation system that streamlines the job application process. It automates job ingestion, filtering, scoring, and generates tailored resumes and cover letters using LLMs (Groq) and LaTeX templates.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Groq API key ([get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Frandiiile/job-hunter-ai.git
   cd job-hunter-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

4. **Verify installation**
   ```bash
   python -m pytest tests/test_imports.py -v
   ```

---

## 📋 Features

- ✅ **Automated Job Ingestion** - Fetch jobs from Adzuna API
- ✅ **Smart Filtering** - Rule-based filtering for junior/mid-level roles
- ✅ **Hybrid Scoring** - Deterministic + LLM scoring (0-100)
- ✅ **AI-Powered Generation** - Tailored CVs and cover letters via Groq LLM
- ✅ **LaTeX Templates** - Professional document rendering
- ✅ **Google Sheets Integration** - Track application pipeline
- ✅ **CI/CD Pipeline** - Automated testing and quality checks
- ✅ **n8n Integration** (Planned) - Full workflow orchestration

---

## 🏗️ Project Structure

```
job-hunter-ai/
├── src/job_hunter_ai/        # Main package
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── scoring.py            # Job scoring logic
│   ├── llm/                  # LLM integration
│   │   ├── groq_client.py    # Groq API client
│   │   └── enrich.py         # CV/cover letter generation
│   ├── latex/                # LaTeX rendering
│   │   └── render_template.py
│   └── drive/                # Google Drive integration
│       └── upload.py
├── scripts/                  # Utility scripts
│   ├── filter_jobs.py        # Job filtering
│   ├── ingest_adzuna_to_sheets.py
│   └── generate_docs_for_job.py
├── profile/                  # Your profile data
│   ├── profile.yml           # Skills, experience, etc.
│   ├── experiences.md        # Work history
│   └── projects.md           # Project descriptions
├── prompts/                  # LLM prompt templates
│   ├── cv_master_prompt.txt
│   ├── cv_one_page_prompt.txt
│   └── cover_letter_prompt.txt
├── templates/                # LaTeX templates
│   ├── cv_template.tex
│   └── cover_template.tex
├── tests/                    # Test suite
│   └── test_imports.py
└── .github/workflows/        # CI/CD
    └── ci.yml
```

---

## 🎯 Usage

### 1. Configure Your Profile

Edit files in the `profile/` directory:
- **profile.yml** - Your skills, experience, location
- **experiences.md** - Detailed work history
- **projects.md** - Technical projects with bullets

### 2. Ingest Jobs

Fetch jobs from Adzuna and save to Google Sheets:
```bash
python scripts/ingest_adzuna_to_sheets.py
```

### 3. Filter Jobs

Apply filtering rules to mark jobs as ready for LLM processing:
```bash
python scripts/filter_jobs.py
```

### 4. Generate Application Documents

For a specific job:
```bash
python scripts/generate_docs_for_job.py
```

This will:
1. Score the job (deterministic + LLM)
2. Generate tailored CV content
3. Generate cover letter
4. Render LaTeX files
5. (Optional) Upload to Google Drive

Generated files will be in `build/jobs/<job_id>/`

---

## 📊 Scoring System

### Hybrid Scoring
Combines deterministic and LLM-based scoring:

```python
final_score = 0.60 * llm_score + 0.40 * deterministic_score
```

### Deterministic Score (0-100)
Based on:
- **Skills overlap** - Match between job requirements and your profile
- **Architecture bonus** (+20 max) - Mentions of your architecture patterns
- **Domain bonus** (+10 max) - Relevant industry experience
- **Seniority penalty** (-20) - Too senior or too many years required

### LLM Score (0-100)
Evaluates:
- Overall fit for the role
- Relevance of your experience
- Project alignment
- Skill transferability

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Test Import Validation
```bash
pytest tests/test_imports.py -v
```

### Test with Coverage
```bash
pytest tests/ --cov=src/job_hunter_ai --cov-report=html
```

---

## 🔧 Development

### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### Set Up Pre-commit Hooks
```bash
pre-commit install
```

### Run Pre-commit Manually
```bash
pre-commit run --all-files
```

### Code Formatting
```bash
black src/ scripts/ tests/
```

### Linting
```bash
flake8 src/ scripts/ tests/ --max-line-length=100
```

---

## 🌐 Environment Variables

Create a `.env` file in the project root:

```bash
# REQUIRED
GROQ_API_KEY=your_groq_api_key_here

# OPTIONAL
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.2
GROQ_TIMEOUT=60

# Adzuna API
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

# Google Sheets
GOOGLE_SHEETS_SPREADSHEET_NAME=job_pipeline
GOOGLE_SHEETS_WORKSHEET_NAME=daily_jobs

# Google Drive (Optional)
# GOOGLE_DRIVE_FOLDER_ID=your_folder_id
# GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
```

---

## 🔄 CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline that runs on every push and pull request:

### Jobs
- **Lint** - Code quality checks (black, flake8)
- **Test** - Unit tests across Python 3.10, 3.11, 3.12 on Ubuntu & Windows
- **Integration** - Import validation and script compilation
- **Security** - Dependency scanning with safety and bandit
- **Build Status** - Overall pipeline status

### View Pipeline
[GitHub Actions](https://github.com/Frandiiile/job-hunter-ai/actions)

---

## 📦 Dependencies

### Core
- `groq` - Groq LLM API client
- `requests` - HTTP requests
- `PyYAML` - Configuration parsing
- `python-dotenv` - Environment variable management

### Google Integration
- `gspread` - Google Sheets API
- `google-auth` - Google authentication

### Development
- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Linter
- `bandit` - Security scanner
- `pre-commit` - Git hooks

See [requirements.txt](requirements.txt) for full list.

---

## 📚 How It Works

1. **Job Ingestion**
   - Fetch jobs from Adzuna API
   - Normalize and deduplicate using SHA-1 hashing
   - Store in Google Sheets with status tracking

2. **Filtering**
   - Apply rule-based filters (seniority, keywords, years)
   - Mark jobs as `NEW`, `SKIPPED`, or `READY_LLM`

3. **Scoring**
   - Calculate deterministic score based on skills overlap
   - Generate LLM score based on semantic fit
   - Combine into hybrid score (bounded ±25 from deterministic)

4. **Document Generation**
   - Generate master CV with all relevant experience
   - Compress to one-page CV optimized for ATS
   - Generate tailored cover letter
   - Render LaTeX templates

5. **Output**
   - `.tex` files ready for compilation or upload to Overleaf
   - Optional Google Drive upload
   - Pipeline tracking in Google Sheets

---

## 🔮 Roadmap

- [ ] n8n workflow orchestration
- [ ] Additional job sources (France Travail, LinkedIn)
- [ ] Auto-apply functionality
- [ ] Email/Telegram notifications
- [ ] PDF compilation automation
- [ ] Web UI dashboard
- [ ] Analytics and reporting

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and linting
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for fast LLM inference
- [Adzuna](https://www.adzuna.com/) for job listing API
- LaTeX community for document templates

---

## 📧 Contact

For questions or issues, please [open an issue](https://github.com/Frandiiile/job-hunter-ai/issues) on GitHub.
