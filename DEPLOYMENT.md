# Deployment Runbook

How the Ask My Docs API is deployed on Render, what it needs, and what to check when it breaks.

---

## Platform

- **Host:** Render, web service
- **Python:** 3.11.9 (set with the `PYTHON_VERSION` environment variable)
- **Live URL:** https://ai-engineer-training.onrender.com
- **Docs page:** https://ai-engineer-training.onrender.com/docs

## Build and start

Render installs dependencies from `pyproject.toml` and then runs:

```bash
uvicorn ai_training.api.main:app --host 0.0.0.0 --port $PORT
```

`$PORT` is supplied by Render. Never hardcode it.

## Environment variables

Set these in the Render dashboard under **Environment**. Never commit them.

| Variable | Required | Purpose |
|---|---|---|
| `GROQ_API_KEY` | Yes | Key for the Groq LLM. The app refuses to start without it. |
| `PYTHON_VERSION` | Yes | Set to `3.11.9` so Render does not use a newer Python. |
| `LOG_LEVEL` | No | `INFO` (default), `WARNING`, `ERROR`. |
| `LLM_MODEL` | No | Default `openai/gpt-oss-20b`. |
| `EMBED_MODEL` | No | Default `all-MiniLM-L6-v2`. |
| `APP_ENV` | No | Default `development`. Use `production` on the server. |

## Pinned dependencies

All versions in `pyproject.toml` are pinned to the exact versions the tests passed with.

Reason: unpinned, Render installs the newest LangChain (1.x), which removed APIs this code uses (`langchain.text_splitter`, `langchain.chains`, `langchain.agents`). The build succeeds but the app crashes at startup with `ModuleNotFoundError`.

When upgrading a library, change the pin, run `pytest -q`, then redeploy.

## Deploying a change

1. Run `pytest -q` locally. All tests must pass.
2. Commit and push to `main`.
3. Render rebuilds automatically.
4. If dependencies changed, use **Manual Deploy > Clear build cache & deploy**.
5. Check the logs for the line `Starting: env=... model=... embed=...`.
6. Call `/health`.

## Health check

```
GET /health  ->  {"status": "ok"}
```

Render calls this repeatedly to confirm the app is alive.

## Logging

The app logs to stdout, which Render shows in **Logs**. Key lines:

- `Starting: env=... model=... embed=...` : startup completed
- `Ingest started: <file> (<n> bytes)` and `Ingest finished: <file> -> <n> chunks`
- `logger.exception` tracebacks for failed ingest, vector store load and LLM calls

The API key is never logged.

## Known limits

- **Memory:** the free tier has 512 MB of RAM. Loading the embedding model (PyTorch and sentence-transformers) exceeds it, so `/ingest` and `/ask` return an empty 502 there. A 2 GB instance is needed, or a hosted embeddings API.
- **Temporary disk:** `artifacts/uploads/` and `artifacts/vector_store/` are wiped on every restart or redeploy. After that, `/ask` returns 404 "Vector store not found" until a document is ingested again.
- **Cold start:** the free tier sleeps when idle, so the first request can take about a minute.
- **Single index:** each `/ingest` rebuilds the vector store from every file in `uploads/`.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Empty 502, log stops after `Ingest started` | Out of memory | Use a 2 GB instance or a hosted embeddings API |
| `ModuleNotFoundError: langchain.text_splitter` | Unpinned LangChain 1.x installed | Pin versions in `pyproject.toml`, clear build cache and redeploy |
| `ImportError: cannot import name ...` at startup | File not pushed to GitHub | `git status`, commit and push the missing file |
| Startup validation error naming `groq_api_key` | `GROQ_API_KEY` not set | Add it in Render **Environment** |
| `/ask` returns 404 "Vector store not found" | Disk was wiped or nothing ingested | Call `/ingest` first |
| `/ask` returns 502 with a JSON body | Groq request failed | Check the traceback in the logs and the Groq key |
| `422` on `/ask` | Missing or blank `question`, or `k` below 1 | Fix the request body |
| `415` on `/ingest` | File is not `.txt` or `.pdf` | Upload a supported type |
| `413` on `/ingest` | File larger than 5 MB | Upload a smaller file |

## Security notes

- Callers cannot choose the vector store path; it is fixed on the server.
- Upload filenames are reduced to their final name part, so `../` paths are ignored.
- Only the filename of each source is returned, never a server path.
- `.env` is gitignored.