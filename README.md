# AI Engineer Training: Summarizer, Ask My Docs (RAG) and Home Control

A Python repo built over a 90-day plan, going from Python basics to deployed LLM applications. It has three projects that share one provider abstraction (Groq or Mock), so models can be swapped without changing application code.

---

## What's inside

| Project | What it does | Interface | Details |
|---|---|---|---|
| Text Summarizer | Summarizes one file or a whole folder in three styles (brief, detailed, bullets) | CLI: `summarize-file`, `batch` | [Usage](#text-summarizer-and-chatbot) |
| Ask My Docs (RAG) | Answers questions about your own documents and cites its sources | CLI: `ingest`, `ask`. API: `/ingest`, `/ask` | [Usage](#ask-my-docs-rag) |
| Home Control | Controls a simulated household in plain English, with confirmation for risky actions and an audit log | API: `/home/command`, `/home/state`, `/home/audit` | [HOME_CONTROL.md](HOME_CONTROL.md) |

The repo also contains an interactive chatbot (`bot` command) with prompt modes and streaming.

---

## Architecture overview

```text
Clients (CLI, HTTP)
  -> FastAPI (/ask, /ingest, /home/*)
  -> Chat / RAG / Agent logic
  -> Provider abstraction (Groq, Mock)
  -> Storage (FAISS vector store, SQLite audit log, files)
```

- **Providers**: `GroqProvider` calls the Groq API. `MockProvider` returns fixed responses, used for tests and for trying the CLI without a key.
- **RAG**: documents are loaded, split into chunks with metadata, embedded (HuggingFace `all-MiniLM-L6-v2`), stored in FAISS, retrieved by similarity, and passed to the LLM with a prompt that says to answer only from the context.
- **Agent**: a tool-calling LLM agent. In Home Control, a guard in code sits between the LLM and the device tools.
- **API**: FastAPI with Pydantic validation and clear status codes.

---

## Quick start

Requires **Python 3.9 or newer**.

```bash
git clone https://github.com/KushalRajMS/ai-engineer-training.git
cd ai-engineer-training
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Try it with the Mock provider. No API key is needed:

```bash
python -m ai_training.cli summarize-file data/inputs/ai_overview.txt --provider mock --style bullets
```

For real model output, create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_key
HOME_API_KEY=a-long-random-string
```

Generate a random key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Never commit `.env`. It is listed in `.gitignore`.

Start the API server:

```bash
uvicorn ai_training.api.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive API documentation.

---

## Tests

```bash
pytest -q
```

The tests use fake LLMs, fake vector stores and temporary databases, so they run without a network connection or API key.

---

## Project docs

- [HOME_CONTROL.md](HOME_CONTROL.md): Home Control architecture, design decisions and limits
- [DEPLOYMENT.md](DEPLOYMENT.md): deploying to Render, environment variables, known limits, troubleshooting

---

## Limits

- The Render free tier has 512 MB of RAM, which is not enough to load the embedding model, so `/ingest` and `/ask` fail there. `/home/*` does not load it.
- The Render free tier disk is temporary. The vector store and the audit log are wiped on restart.
- Home Control devices are simulated, and the API key is one shared secret, not per-user accounts.
- Local development was done on Python 3.9. The Render deployment uses Python 3.11.9 with pinned dependencies.

---

# Usage reference

## Text Summarizer and Chatbot

**Summarize a file:**

```bash
python -m ai_training.cli summarize-file data/inputs/ai_overview.txt --provider groq --style brief
python -m ai_training.cli summarize-file data/inputs/python_intro.txt --provider mock --style bullets
```

**Summarize every file in a folder:**

```bash
python -m ai_training.cli batch data/inputs/ --provider mock --style detailed --output-dir artifacts/
```

**Chat:**

```bash
python -m ai_training.cli bot --provider groq --prompt-mode default
python -m ai_training.cli bot --provider mock --stream
```

| Option | Commands | Meaning |
|---|---|---|
| `--provider` | `bot`, `summarize-file`, `batch` | `groq` or `mock` |
| `--model` | `bot`, `summarize-file`, `batch` | Model name (Groq only) |
| `--style` | `summarize-file`, `batch` | `brief`, `detailed` or `bullets` |
| `--prompt-mode` | `bot` | `default`, `technical_writer`, `data_analyst` or `code_reviewer` |
| `--stream` | `bot` | Print the reply as it is generated |
| `--output-dir` | `batch` | Where result files are saved |

## Ask My Docs (RAG)

Step 1: ingest your documents once. This builds and saves the vector store.

```bash
python -m ai_training.cli ingest --source data/inputs/ --store artifacts/vector_store/
```

Step 2: ask questions. Each query loads the saved store.

```bash
python -m ai_training.cli ask "What is Python?" --store artifacts/vector_store/
python -m ai_training.cli ask "What is AI?" --store artifacts/vector_store/ --k 2
```

Example output:

```text
Answer:
Python is a high-level programming language known for its simple and readable syntax...

Sources:
- data/inputs/python_intro.txt (chunk 0)
- data/inputs/ai_overview.txt (chunk 1)
```

Through the API, `POST /ingest` uploads a `.txt` or `.pdf` file (up to 5 MB) and rebuilds the store, and `POST /ask` takes `{"question": "...", "k": 3}`. Only filenames are returned as sources, never server paths.

## Error handling

| Scenario | Behaviour |
|---|---|
| `ask` before `ingest` | Prints the missing path and the `ingest` command to run |
| Empty question | Clear message, exits cleanly (API returns 422) |
| Empty file in the documents folder | Skipped during ingestion |
| Unknown provider | Lists valid options, exits with code 1 |
| Unknown prompt mode | Warning printed, falls back to default |
| Failed summarization | Marked as failed in the batch report, the batch continues |
| Answer not in the documents | The prompt tells the model to say "I don't know" |
| API: unsupported file type or oversize upload | 415 or 413 |

## Project structure

```text
src/ai_training/
  chat/               chatbot, sessions, prompt profiles
  providers/          Groq and Mock providers (common interface)
  pipeline/           file loading, summarizing, output writing
  langchain_basics/   loaders, splitters, embeddings, vector store,
                      RAG, memory retriever, tools, agent
  home/               Home Control: devices, guarded agent, audit log, API router
  api/                FastAPI app, models, services
  cli.py              terminal commands
  settings.py         typed settings
data/inputs/          sample documents
artifacts/            generated outputs
tests/                unit tests
```