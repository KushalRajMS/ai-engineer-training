# AI Engineer Training: Chatbot, Summarizer and Ask My Docs (RAG)

A Python command-line toolkit built during a 90-day GenAI Engineer training plan. It includes an interactive chatbot, single-file and batch summarization, and **Ask My Docs**, a RAG app that answers questions about your own documents and cites its sources. Everything runs behind a provider abstraction (Groq and Mock), so you can switch models without changing application code.

---

## Projects

| Project | What it does | Commands |
|---|---|---|
| Chatbot | Multi-turn chat with prompt modes and streaming | `bot` |
| Text Summarizer | Summarizes one file or a whole folder in three styles | `summarize-file`, `batch` |
| Ask My Docs (RAG) | Answers questions from your documents, with sources | `ingest`, `ask` |

---

## Architecture

### Chatbot and Summarizer

```text
CLI (typer)
  -> ChatBot / Summarizer
    -> Provider (Groq / Mock)
      -> ChatSession (history, windowing, metadata)
        -> OutputWriter (artifacts/)
```

- **CLI**: entry point for all commands
- **ChatBot**: manages conversation state and provider calls
- **Summarizer**: builds prompts and processes file content
- **Provider**: abstraction layer; swap Groq for Mock without changing anything else
- **ChatSession**: stores history, windowing, and metadata
- **OutputWriter**: persists results to `artifacts/`

### Ask My Docs (RAG)

```text
Ingest (run once)
  Documents (.txt / .pdf)
    -> Loaders
    -> Text splitter (chunks + metadata)
    -> Embeddings (HuggingFace all-MiniLM-L6-v2)
    -> FAISS vector store (saved to disk)

Ask (run many times)
  Question
    -> Load vector store
    -> Retriever (top-k similar chunks)
    -> Prompt with context
    -> LLM (Groq)
    -> Answer + sources
```

- **Loaders**: read files into LangChain `Document` objects
- **Splitter**: breaks documents into overlapping chunks and tags each with source, chunk index and doc id
- **Embeddings**: turn each chunk into a vector that captures its meaning
- **FAISS**: stores vectors locally and finds the chunks closest in meaning to a question
- **Retriever**: returns the top-k chunks for a question
- **RAG prompt**: tells the LLM to answer only from the retrieved context, and to say "I don't know" otherwise
- **Sources**: the metadata of the retrieved chunks, shown with every answer

The repo also contains a conversation-memory retriever (follow-up questions are rewritten using chat history) and a tool-calling agent with normalized tool outputs, built as part of the training plan.

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

```text
GROQ_API_KEY=your_key_here
LLM_MODEL=openai/gpt-oss-20b
LC_TEMPERATURE=0
```

Never commit `.env`. It is listed in `.gitignore`.

---

## Usage

### Ask My Docs (RAG)

Step 1: ingest your documents once. This builds and saves the vector store.

```bash
python -m ai_training.cli ingest --source data/inputs/ --store artifacts/vector_store/
```

Step 2: ask questions. Each query loads the saved store, so it is fast.

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

| Option | Command | Meaning |
|---|---|---|
| `--source` | `ingest` | Folder or file to load (`.txt`, `.pdf`) |
| `--store` | `ingest`, `ask` | Where the vector store is saved or loaded from |
| `--k` | `ask` | Number of chunks to retrieve (default 3) |

### Chat

```bash
python -m ai_training.cli bot --provider groq --prompt-mode default
python -m ai_training.cli bot --provider mock --stream
```

### Summarize a file

```bash
python -m ai_training.cli summarize-file data/inputs/ai_overview.txt --provider groq --style brief
python -m ai_training.cli summarize-file data/inputs/python_intro.txt --provider mock --style bullets
```

### Batch summarize

```bash
python -m ai_training.cli batch data/inputs/ --provider mock --style detailed --output-dir artifacts/
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| `ask` before `ingest` (no vector store) | Prints the missing path and the exact `ingest` command to run |
| Empty question passed to `ask` | Prints "Question can not be blank or empty." and exits cleanly |
| Empty file in the documents folder | Skipped during ingestion; other files still load |
| File not found (summarizer) | Clear message printed, exits cleanly |
| Unknown provider | Lists valid options, exits with code 1 |
| Unknown prompt mode | Warning printed, falls back to default |
| Empty chat input | ValueError caught, error message printed |
| Failed summarization | Marked as failed in the report, batch continues |
| Answer not in the documents | The prompt instructs the model to reply "I don't know" instead of guessing |

---

## Run Tests

```bash
pytest --tb=short
```

Unit tests use fake providers, retrievers and vector stores, so they run without network access or API keys.

---

## Project Structure

```text
src/ai_training/
  chat/               chatbot, sessions, prompt profiles
  providers/          Groq and Mock providers (common interface)
  pipeline/           file loading, summarizing, output writing
  langchain_basics/   loaders, splitters, embeddings, vector store,
                      RAG, memory retriever, tools, agent
  cli.py              all terminal commands
data/inputs/          sample documents
artifacts/            generated outputs
tests/                unit tests
```

---

## Sample Inputs

Sample documents are in `data/inputs/`. Run any command above against them right after setup.