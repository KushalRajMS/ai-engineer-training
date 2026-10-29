# GenAI Engineer Training Tracker

## Purpose
This repository is the rebuild of the 90-day GenAI application engineering plan using practical, real-world open-source and local AI workflows instead of only pre-coded responses.

This file is the master tracker for setup, milestones, daily progress, evidence, and review gates.

---

## 1. Project Goal

Become job-ready as a GenAI Engineer who builds and ships applications in Python with:
- local/open-source LLM usage
- provider abstraction
- chat flows and memory
- prompt control
- structured outputs
- file processing pipelines
- RAG and retrieval
- simple agents
- CLI and basic API work
- deployment awareness
- portfolio narratives and proof

The goal is not to memorize theory; it is to build working systems and keep evidence of each milestone.

---

## 2. Setup Decision

We will prefer a practical setup that works on your Mac without requiring a paid API for the entire training.

Primary path:
- Python 3.11 or 3.12
- VS Code
- Git
- Local open-source LLMs via Ollama
- Mock provider for deterministic testing
- Paid cloud APIs are optional and are not required

This keeps the learning grounded in real-world conditions while remaining runnable in local/offline environments.

---

## 3. Required Tools and Installation Checklist

### 3.1 VS Code
Install VS Code from the official site if not already present.

Recommended extensions:
- Python
- Pylance
- Python Environments
- Ruff
- GitLens
- Docker (optional)

### 3.2 Git
Check:
```bash
git --version
```
If missing, install Git for macOS.

### 3.3 Python
Check:
```bash
python3 --version
```
Expected: Python 3.11 or 3.12.

If missing:
- Use Python.org installer or
- Use `pyenv` if preferred

### 3.4 Ollama (recommended local LLM runtime)
Install Ollama from the official website or shell instructions.

Verify:
```bash
ollama --version
```

Common local model usage:
```bash
ollama pull llama3.1
ollama pull mistral
ollama pull qwen2.5
```

Use these as the local model backend for realistic experiments.

### 3.5 Virtual Environment
Create a project environment:
```bash
cd ~/Desktop/ai-engineer-training
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Check:
```bash
python -m pip --version
```

### 3.6 Project Dependencies
Install the baseline toolchain:
```bash
python -m pip install httpx python-dotenv pydantic tenacity pytest pytest-cov ruff typer rich
```

For later phases:
```bash
python -m pip install langchain langchain-community langchain-openai chromadb sentence-transformers pypdf python-docx fastapi uvicorn
```

---

## 4. Repository Structure

```text
ai-engineer-training/
├── README.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── src/
│   └── ai_training/
│       ├── __init__.py
│       ├── config.py
│       ├── logging_config.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── mock.py
│       │   └── real.py
│       ├── chat/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── session.py
│       │   ├── prompts.py
│       │   └── parser.py
│       ├── pipelines/
│       ├── rag/
│       ├── agents/
│       └── api/
├── cli/
├── tests/
├── data/
│   ├── inputs/
│   └── outputs/
├── artifacts/
├── projects/
│   ├── text_summarizer/
│   ├── ask_my_docs/
│   └── original_project/
└── AI_ENGINEER_TRAINING_TRACKER.md
```

---

## 5. Core Design Principles

Every project build must follow these rules:

1. Define input-output contract before coding.
2. Keep provider abstraction intact.
3. Handle error paths explicitly.
4. Save run artifacts for evidence.
5. No progression without review.
6. No silent bad data use.
7. Prefer local/open-source models during learning.
8. Use real integrations, not only mocked examples.

---

## 6. Universal Pass Checklist

Every day, evaluate the work against these checks:

- Happy path works
- Failure path handled
- Empty/invalid input does not crash
- Output format is consistent
- Code is clear enough to explain in interviews
- Evidence is saved in `artifacts/` or project outputs

---

## 7. Daily Execution Protocol

For every daily milestone:

1. Define objective.
2. Define input and output contract.
3. Build smallest complete slice.
4. Run success case.
5. Run failure case.
6. Review and fix.
7. Save output evidence.
8. Mark complete only after pass.

### Teaching rules

- Give the complete current day's learning and development task together.
- Keep the task realistic for 1-2 hours.
- Explain the concepts, purpose, data flow, task, tests, and pass criteria before coding.
- The learner writes the implementation; review gives targeted corrections instead of copy-paste solutions.
- Do not give the next day until the current day's code has been checked and run successfully.
- Update this tracker after meaningful progress and clearly report what changed.
- Keep the end goal visible: become a GenAI Engineer who builds applications.
- **Before providing any task:** Check the current codebase. Understand what is already implemented. Provide only the actual development work needed. Do not assign duplicate work or tasks for already-completed code.

---

## 8. Full 90-Day Plan

## Phase 1: Days 1-20, Python for AI foundations

### Outcomes
- function design, parameters, data flow
- error handling patterns
- file read/write and JSON handling
- module/package structure
- environment variables and secrets basics
- HTTP request fundamentals
- class-based state handling
- simple chat session object model

### Required project setup
- Python environment and package structure
- config loader
- JSON persistence helpers
- simple logging
- test setup
- mock data and fail-safe behavior

### Pass conditions
- You can build and debug medium-size Python scripts.
- You can safely parse external data.
- You can persist app state.

### Daily evidence to keep
- small scripts or modules in `src/`
- test results from `pytest`
- sample output files in `artifacts/`

---

## Phase 2: Days 21-45, LLM app fundamentals and first real product

### Block A: Days 21-23, Chat Core with a Local Open-Source Model
Build:
- provider interface
- mock provider and Ollama provider path
- message contract
- single-turn and multi-turn chat loop
- safe response extraction from nested JSON

Pass criteria:
- chat works in mock mode and Ollama mode with a config switch
- empty input and malformed response do not crash
- history grows correctly

### Day 21 Current Status

**COMPLETE** ✅

Completed:
- project package and editable install
- provider contract and mock provider
- message model and session history basics
- single-turn chatbot flow
- empty and whitespace input validation
- custom provider injection
- **multi-turn flow using one `ChatSession`** ✅
- **assistant response added back into session history** ✅
- **verified second provider request receives earlier conversation context** ✅
- **verified user and assistant messages remain in correct order** ✅
- **verified history limit during multi-turn flow** ✅
- **explicit provider-failure behavior defined and tested** ✅
- **Ollama installed, mistral model downloaded** ✅
- **OllamaProvider implementation complete** ✅
- **chat flow tested in mock mode and Ollama mode** ✅
- **8 passing tests** ✅

Evidence:
- All 8 pytest tests passing (2026-08-29)
- chatbot.py: multi-turn session reuse with history trimming
- ollama.py: HTTP integration with Mistral on localhost:11434
- Test coverage: empty input validation, provider injection, multi-turn history growth, Ollama integration

### Day 22 Current Status

**Objective:** Provider resilience and error handling

**Input/Output Contract:**
- Input: messages list (dict with role and content)
- Output: response string OR raises ValueError with clear message
- Error cases: timeout, connection refused, invalid JSON, missing response field

**Build:**
- Timeout handling in OllamaProvider (httpx timeout is set, but needs validation)
- Connection error handling (Ollama not running)
- Malformed JSON response handling
- Missing "response" field in JSON handling
- Optional: retry logic for transient failures
- Tests for all failure paths

**Pass criteria:**
- Timeout: response within 60 seconds or raises TimeoutError
- Connection refused: raises ValueError("Cannot connect to Ollama")
- Malformed JSON: raises ValueError("Invalid response from Ollama")
- Missing field: raises ValueError("Ollama response missing 'response' field")
- All error scenarios tested and passing

**Day 22 evidence:**
- Tests for timeout scenario
- Tests for connection failure
- Tests for malformed JSON
- Tests for missing field
- Passing test output showing all failures handled

---

### Day 23 Current Status

**Objective:** Interactive multi-turn chat demo with conversation history

**Build:**
- Interactive CLI script (simple loop: input → response → repeat)
- Session persistence across turns (same ChatSession object)
- Save conversation to artifacts/ as JSON
- Support both MockProvider and OllamaProvider
- Exit command to quit gracefully

**Input/Output Contract:**
- Input: User text in terminal
- Output: Model response printed to terminal
- Side effect: Conversation saved to `artifacts/chat_history_{timestamp}.json`

**Script flow:**
1. Ask user to pick provider (mock or ollama)
2. Initialize ChatSession
3. Loop: get user input → call chat_once() → print response → save to session
4. User types "exit" to quit
5. Save final conversation to JSON file

**Pass criteria:**
- User can have 3+ turn conversation without crash
- Conversation history is saved to file
- Both Mock and Ollama modes work
- Exit command works cleanly
- Saved JSON is valid format

**Day 23 evidence:**
- Sample conversation output in artifacts/
- JSON file with complete history
- Interactive demo runs without errors

---

## Progress Update: Days 24-38

### Days 24-26 — Prompt Control and Memory

**COMPLETE** ✅

- Added named prompt profiles and system-prompt selection.
- Preserved the system message when clearing or trimming conversation history.
- Added a sliding message window for provider requests while retaining full saved history.
- Added timestamps to `Message` objects and lightweight session metadata, including estimated token counts.
- Kept timestamp metadata out of provider payloads so JSON API requests remain serializable.

### Days 27-29 — Structured Output and Retry

**COMPLETE** ✅

- Built few-shot prompt construction for instruction-only, examples-only, combined, and fallback cases.
- Added JSON response parsing and required-field validation.
- Added retry-based structured extraction with escalating instructions and deterministic stub-provider tests.
- Verified structured extraction against Groq and covered success, eventual-success, and total-failure paths.

### Days 30-32 — File and LLM Pipeline

**COMPLETE** ✅

- Added recursive `.txt` file discovery, safe text loading, and per-file failure isolation.
- Added single-file and batch summarization through the provider abstraction.
- Added versioned JSON result persistence, output-directory creation, and batch reports.
- Verified that one unreadable or invalid file does not stop the remaining batch.

### Days 33-35 — ChatBot Class Refactor

**COMPLETE** ✅

- Added `ChatBot` as a stateful wrapper around the existing functional chat flow.
- Added history access, memory clearing, provider switching, and prompt-mode switching.
- Verified the class and original function-based API produce the same responses and history behavior with `MockProvider`.

### Day 36 — Initial Typer CLI

**COMPLETE** ✅

- Added `bot`, `summarize-file`, and `batch` terminal commands in `ai_training.cli`.
- Wired commands to `ChatBot`, `FileLoader`, `Summarizer`, and `OutputWriter`.
- Manually verified interactive chat, single-file summary, and batch summary workflows.

### Day 37 — Configurable CLI Flags

**COMPLETE** ✅

- Added `--provider`, `--model`, `--prompt-mode`, and `--output-dir` support in the appropriate commands.
- Added lazy provider selection for Groq and Mock providers.
- Added CLI tests for chat, invalid provider handling, single-file summarization, and custom batch output directories.
- Verified five CLI tests passed.

### Day 38 — CLI Help and Structured Output

**COMPLETE** ✅

- Added application, command, argument, and option help text.
- Standardized successful `summarize-file` output as JSON containing `filename`, `summary`, and `success`.
- Standardized successful `batch` output as JSON containing an overall `report` and per-file `results`.
- Updated CLI tests to parse JSON output with `json.loads()` and validate the output contract.
- Manually verified root and command-level `--help` menus.
- Full test suite evidence: **40 passed in 2.75 seconds** on Python 3.9.6 / pytest 8.4.2 (2026-09-21).

---

### Block B: Days 24-26, Prompt Control and Memory
Build:
- prompt library with named profiles
- system prompt selection per mode
- sliding history window
- lightweight summary metadata

Pass criteria:
- mode switch changes behavior
- last-N window enforced
- prompt selection centralized

### Block C: Days 27-29, Structured Output
Build:
- few-shot pattern examples
- strict JSON output prompting
- output validator for required keys and types
- retry logic for invalid response format

Pass criteria:
- parse succeeds repeatedly
- invalid output caught gracefully
- required fields validated before use

### Block D: Days 30-32, File + LLM Pipeline
Build:
- input loader for text files
- summarize/extract pipeline
- output persistence to JSON and text
- batch processing

Pass criteria:
- per-file success/failure report
- readable output files
- one broken input does not stop the whole batch

### Block E: Days 33-35, Class Refactor
Build:
- chatbot class wrapping provider, prompt, memory, parsing
- cleaner state encapsulation
- reusable methods

Pass criteria:
- same behavior as function-based version
- cleaner interface
- unit checks on class methods

### Block F: Days 36-38, CLI Tooling
Build:
- argparse or typer CLI
- flags for provider, model, prompt mode, input file
- structured CLI output

Pass criteria:
- help menu clear
- invalid flags handled gracefully
- workflows run from command line

### Block G: Days 39-41, Streaming
Build:
- streaming response handling
- token/chunk rendering
- final aggregation and persistence

Pass criteria:
- stream and non-stream both work
- partial chunks do not corrupt final result

### Block H: Days 42-45, Project 1
Build:
- AI Text Summarizer end-to-end
- configurable prompt style
- batch mode
- README with run instructions and architecture

Pass criteria:
- runnable from clean clone
- sample input/output included
- error paths demonstrated

---

## Phase 3: Days 46-70, LangChain, RAG, Agents

### Block A: Days 46-48, LangChain Basics
Build:
- PromptTemplate and chain flow
- side-by-side raw SDK vs chain abstraction
- consistent configuration

### Block B: Days 49-52, Document Ingestion
Build:
- loaders for txt/pdf/docs
- splitter experiments
- chunk metadata tracking

### Block C: Days 53-56, Embeddings and Store
Build:
- embedding pipeline
- vector store creation and persistence
- similarity retrieval basics

### Block D: Days 57-60, RAG Core
Build:
- retriever + generator pipeline
- source grounding
- prompt with context injection

### Block E: Days 61-63, Conversation Memory in RAG
Build:
- follow-up memory handling
- balance between history and retrieved context
- drift control

### Block F: Days 64-67, Agent Patterns
Build:
- tool registry
- ReAct-like loop
- tool output normalization

### Block G: Days 68-70, Project 2
Build:
- Ask My Docs RAG app
- ingestion command and query command
- docs and demo evidence

---

## Phase 4: Days 71-90, Productization and Hiring

### Block A: Days 71-75, FastAPI
Build:
- chat or query endpoints
- validated request/response schemas
- error contract and status codes

### Block B: Days 76-78, Deployment
Build:
- environment-based config
- logging and startup checks
- deployment runbook

### Block C: Days 79-82, Original Project 3
Build:
- your own AI product idea
- end-to-end architecture
- production-style reliability controls

### Block D: Days 83-85, Repo Polish
Build:
- polished README
- architecture diagrams
- setup instructions from zero
- troubleshooting guide

### Block E: Days 86-88, Public Proof
Build:
- technical posts
- project-specific lessons and tradeoffs

### Block F: Days 89-90, Applications
Build:
- role list
- resume bullets mapping to projects
- outreach and tracking

---

## 9. Open-Source / Real-World Guidance

Since you want real-world experience, do not rely only on pre-coded responses.

Use these as preferred paths:
- local open-source LLM via Ollama for real model experiments
- Ollama's OpenAI-compatible API when an SDK-style interface is useful
- paid model APIs only as optional comparisons, never as a requirement
- mock provider for deterministic unit tests and reliability checks
- real document ingestion with PDFs/TXT/DOCX for RAG
- real batch processing inputs
- persisted outputs and logs for evidence

Avoid:
- building only in notebooks without reusable modules
- skipping failure cases
- building a front-end before core logic works
- trusting model output without validation

---

## 10. GitHub and Portfolio Evidence

GitHub publishing is allowed because this training is being rebuilt on your personal local Mac.

For portfolio projects:
- keep the code in a Git repository
- push completed projects to GitHub
- include a README with setup, architecture, usage, tests, and failure handling
- include safe sample inputs and outputs

Never publish secrets, `.env` files, private company data, or personal credentials.

---

## 11. Required Daily Logging Format

Every day, log:

### Daily Template
```text
Date:
Objective:
Input contract:
Output contract:
What built:
Success test:
Failure test:
Error found:
Fix made:
Evidence saved:
Pass/Fail:
Next step:
```

---

## 11. Suggested Start Sequence

This is the practical order to begin:

1. Confirm Python, Git, VS Code are working.
2. Set up virtual environment.
3. Install base dependencies.
4. Create config and logging module.
5. Create mock provider and provider interface.
6. Create message model and chat loop.
7. Test happy path and failure path.
8. Save artifacts.
9. Move to prompt control and memory.
10. Move to structured output validation.
11. Build file intake and summarization.
12. Move to CLI.
13. Build first end-to-end project.

---

## 12. Daily Work Philosophy

You are not simply following a checklist. You are building a portfolio-quality learning system.

This means each day must show:
- code that solves a realistic problem
- validation of correct behavior
- failure handling with evidence
- explanation in interview language
- saved artifacts proving it works

---

## 13. First Actions to Do

Run these in your terminal once the virtual environment is ready:

```bash
cd ~/Desktop/ai-engineer-training
source .venv/bin/activate
python -V
pip install --upgrade pip
pip install httpx python-dotenv pydantic tenacity pytest pytest-cov ruff typer rich
```

Then create:
- `src/ai_training/__init__.py`
- `src/ai_training/config.py`
- `src/ai_training/logging_config.py`

After that, build the first core modules:
- provider interface
- mock provider
- message schema
- session history management

---

## 14. Permission Gate Before Further Tools

Before installing anything heavy or changing system config beyond Python tooling, ask for confirmation if the environment is not already ready.

The only actions allowed without further permission are:
- creating project folders
- creating markdown files
- editing tracker notes
- writing code in the project repository

The following actions require explicit permission or user execution:
- installing system packages with package managers
- installing Ollama or any external runtime
- installing Docker
- installing cloud SDKs
- creating secrets or API keys
- running model downloads that consume bandwidth or disk space

---

## 15. Current Status

Status: **Complete through Day 38 — CLI Tooling block complete.**

Next recommended action:
- Start Day 39: streaming responses from the provider.
- Preserve both stream and non-stream paths while adding chunk-by-chunk terminal rendering.

---

## 16. Evidence Folder

Use this folder for all run outputs:
```text
artifacts/
```

Examples:
- `artifacts/chat_success.json`
- `artifacts/invalid_response_example.json`
- `artifacts/summarizer_run_01.txt`
- `artifacts/batch_summary_report.json`

Keep actual outputs in the repository so they count as evidence.

---

## 17. Important Reminder

You already did the training plan. Now the rebuild is about practical implementation in this machine.

The work should be built with:
- local/open-source AI first
- provider abstraction second
- real file and document workflows third
- API and deployment only after the core works

This is the correct path for job readiness.
