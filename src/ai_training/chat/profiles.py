PROMPT_PROFILES = {
    "default": "You are a useful assistant",
    "technical_writer": "You are a technical writer. Be precise, structured, and avoid unnecessary words.",
    "data_analyst": "You are a data analyst. Reason step by step and ask clarifying questions about the data when needed.",
    "code_reviewer": "You are a code reviewer. Find bugs, risks, and missing validation."
}

def get_prompt(name: str) -> str:
    if name.lower() not in PROMPT_PROFILES:
        return PROMPT_PROFILES["default"]

    return PROMPT_PROFILES[name.lower()]