# ChatBot — AI Engineer Training Project

A command-line AI application built in Python that supports interactive chat, single-file summarization, and batch summarization using provider abstraction (Groq and Mock). Built as part of a 90-day GenAI Engineer training plan.

---

## Architecture

CLI (typer)
→ ChatBot / Summarizer
→ Provider (Groq / Mock)
→ ChatSession (history, windowing, metadata)
→ OutputWriter (artifacts/)


- **CLI** — entry point for all commands
- **ChatBot** — manages conversation state and provider calls
- **Summarizer** — builds prompts and processes file content
- **Provider** — abstraction layer; swap Groq for Mock without changing anything else
- **ChatSession** — stores history, windowing, and metadata
- **OutputWriter** — persists results to `artifacts/`

---

## Setup

```bash
git clone https://github.com/KushalRajMS/ai-engineer-training.git
cd ai-engineer-training
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Create a `.env` file in the project root:

GROQ_API_KEY=your_key_here


---

## Usage

**Chat:**
```bash
python -m ai_training.cli bot --provider groq --prompt-mode default
python -m ai_training.cli bot --provider mock --stream
```

**Summarize a file:**
```bash
python -m ai_training.cli summarize-file data/inputs/ai_overview.txt --provider groq --style brief
python -m ai_training.cli summarize-file data/inputs/python_intro.txt --provider mock --style bullets
```

**Batch summarize:**
```bash
python -m ai_training.cli batch data/inputs/ --provider mock --style detailed --output-dir artifacts/
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| File not found | Clear message printed, exits cleanly |
| Unknown provider | Lists valid options, exits with code 1 |
| Unknown prompt mode | Warning printed, falls back to default |
| Empty input | ValueError caught, error message printed |
| Failed summarization | Marked as failed in report, batch continues |

---

## Run Tests

```bash
pytest --tb=short
```

---

## Sample Inputs

Sample input files are in `data/inputs/`. Run any command above against them immediately after setup.