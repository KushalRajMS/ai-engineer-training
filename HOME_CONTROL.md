# Home Control: natural-language control with safety controls

A console that lets a user control a household in plain English ("turn on the kitchen light and unlock the front door") from any client that can call an HTTP API. Risky actions need explicit confirmation, and every action is written to an audit log.

Devices are simulated. The device layer sits behind an interface, so a real system (Home Assistant, MQTT) can replace the simulator without changing the rest.

---

## Architecture

```text
Phone / client app
  -> FastAPI  (/home/command, /home/state, /home/audit)
       -> X-API-Key check (constant-time compare)
       -> Pydantic validation (blank text / session id -> 422)
       -> get_agent(session_id)          one HomeAgent per session
            -> HomeAgent (LLM + guarded tools)
                 -> guard: is_risky(tool, args)?
                      safe  -> run tool
                      risky -> store as pending, ask the user to confirm
                 -> DeviceController interface
                      -> SimulatedHome (lights, doors, thermostat)
            -> Audit log (SQLite): every blocked, confirmed and safe action
```

- **API layer**: authentication, validation, status codes.
- **HomeAgent**: a tool-calling LLM agent that turns text into tool calls.
- **Guard**: sits between the LLM and the tools. The LLM never calls a real tool directly.
- **DeviceController**: the contract for any device backend.
- **Audit log**: append-only history in SQLite.

---

## Design decisions

| Decision | Reason |
|---|---|
| Device layer behind an abstract interface (`DeviceController`) | A real device backend can replace `SimulatedHome` without touching the agent or API. |
| Confirmation enforced in code, not in the prompt | A prompt is a request to the model, code is a guarantee. The LLM can forget or be talked out of asking, but it cannot run an unlock itself. |
| Only unlocking is risky (`is_risky` checks arguments) | Locking is the safe direction. Confirming every lock would train users to click "yes" without reading. |
| Pending action expires after 60 seconds | A forgotten unlock request cannot be confirmed later by an unrelated "ok". |
| Ambiguous replies keep the pending action and never reach the LLM | Only a clear yes runs it. Anything else re-prompts. |
| One `HomeAgent` per `session_id` | One session's "yes" cannot confirm another session's unlock. |
| Audit is written in the tool layer | That is the only place that knows an action really ran, so the log cannot disagree with reality. |
| Blocked attempts are logged too | "Someone asked to unlock the door and was prompted" is useful security history. |
| API key checked with `secrets.compare_digest`; all requests rejected if no key is set | Constant-time comparison avoids timing leaks. A missing key means locked, not open. |
| Tools return `{tool_name, result, success}` instead of raising | One failed device does not stop the others in the same request. |
| SQLite for the audit log | It survives restarts and needs no server. Parameterised queries prevent SQL injection. |
| No vector database | The problem is tool choice and device state, not semantic search. A vector store would be added for manual Q&A or user routines. |

---

## Setup

```bash
git clone https://github.com/KushalRajMS/ai-engineer-training.git
cd ai-engineer-training
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Create `.env` in the project root:

```text
GROQ_API_KEY=your_groq_key
HOME_API_KEY=a-long-random-string
```

Generate a key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Start the server:

```bash
uvicorn ai_training.api.main:app --reload
```

---

## Usage

Load the key into a shell variable:

```bash
KEY=$(grep HOME_API_KEY .env | cut -d= -f2)
```

Send a safe command:

```bash
curl -X POST http://127.0.0.1:8000/home/command \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"session_id": "phone-1", "text": "turn on the kitchen light"}'
```

Request a risky action. The door is not unlocked yet:

```bash
curl -X POST http://127.0.0.1:8000/home/command \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"session_id": "phone-1", "text": "unlock the front door"}'
```

```json
{"reply":"I'm ready to unlock the front door, but I need your confirmation first. Is that okay?","needs_confirmation":true}
```

Confirm in the same session:

```bash
curl -X POST http://127.0.0.1:8000/home/command \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"session_id": "phone-1", "text": "yes"}'
```

Read the state and the audit trail:

```bash
curl http://127.0.0.1:8000/home/state -H "X-API-Key: $KEY"
curl "http://127.0.0.1:8000/home/audit?limit=20" -H "X-API-Key: $KEY"
```

The audit shows two rows for one unlock: the blocked request (`success: 0`), then the confirmed execution (`success: 1`).

### Endpoints

| Method | Path | Purpose | Errors |
|---|---|---|---|
| POST | `/home/command` | Send a text command | 401 bad key, 422 blank input, 502 agent failure |
| GET | `/home/state` | Current state of all devices | 401 |
| GET | `/home/audit?limit=50` | Recent actions, newest first (limit 1 to 500) | 401, 422 |

---

## Reliability behaviour

- Invalid input (unknown room, thermostat outside 10 to 30) returns `success: false`, never a crash.
- An offline device reports its failure while the other devices in the same request still work.
- An unexpected tool exception is caught and recorded in the audit log.
- Failed agent calls return 502 and the traceback goes to the server log only.

---

## Tests

```bash
pytest -q
```

Tests use a fake LLM and temporary databases, so they need no network or API key. They prove that:

- A risky call does not change the device before confirmation.
- A clear yes runs the pending action once, and a clear no cancels it.
- Ambiguous replies never run the action.
- Pending actions expire after 60 seconds.
- Session B cannot confirm session A's unlock.
- A safe tool runs exactly once.
- The audit log records the blocked request, then the confirmed one.
- Requests without the key get 401, and blank fields get 422.
- An offline device fails alone.

---

## Limits

- **One shared API key**: it identifies the client, not a person. Per-user accounts would be the next step.
- **Sessions in memory**: a restart forgets pending confirmations. They expire in 60 seconds anyway.
- **Simulated devices**: state resets on restart. A real backend would hold its own state.
- **SQLite on Render's free tier**: the disk is temporary, so the audit log is wiped on restart. Production needs a persistent disk or hosted Postgres.
- **Single process**: SQLite writes and the in-memory session dict assume one server process.
- **LLM dependence**: the agent needs the Groq API. The guard still prevents unconfirmed unlocks if the model misbehaves.