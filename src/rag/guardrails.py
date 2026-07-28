import re
import unicodedata

# Blacklist patterns for system commands, prompt injection, and code injection
SUSPICIOUS_PATTERNS = [
    r"rm\s+-rf",
    r"sudo\s+",
    r"drop\s+database",
    r"drop\s+table",
    r"import\s+os",
    r"import\s+sys",
    r"exec\s*\(",
    r"eval\s*\(",
    r"ignore\s+previous\s+instructions",
    r"system\s+prompt",
    r"you\s+are\s+now\s+a",
    r"forget\s+(your|all)\s+instructions",
    r"ignoriere\s+alle\s+anweisungen",
]


def check_input_safety(query: str) -> tuple[bool, str | None]:
    """Inspects user input for dangerous commands or injection attempts.
    
    Returns:
        tuple[bool, str | None]: (is_safe, refusal_reason)
    """
    # Normalize unicode to handle accented characters and potential lookalikes
    normalized_query = unicodedata.normalize("NFKD", query).lower()

    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, normalized_query):
            return False, f"Input contained prohibited pattern/command: '{pattern}'"

    return True, None