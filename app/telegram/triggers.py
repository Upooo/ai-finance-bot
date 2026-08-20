import re

from app.config import BOT_NAMES, DISMISS_PHRASES

# Words that signal the user is *addressing* the bot
CALLING_WORDS = [
    "woi", "woy", "hei", "hey", "hai", "hi", "oi", "oy", "yo",
    "tolong", "dong", "coba", "bisa", "minta", "please",
    "eh", "duh", "bang", "kak", "min",
]


def should_respond(text: str, bot_username: str = None) -> bool:
    """Return True if the message is calling / addressing the bot."""
    if not text:
        return False

    low = text.lower().strip()

    # @mention always triggers
    if bot_username and f"@{bot_username.lower()}" in low:
        return True

    # Check if any bot name appears
    has_name = any(name in low for name in BOT_NAMES)
    if not has_name:
        return False

    words = low.split()

    # Single word "idol" alone -> don't respond
    if len(words) <= 1:
        return False

    # Calling word present -> respond
    if any(w in low for w in CALLING_WORDS):
        return True

    # Bot name at start/end with more content -> respond
    for name in BOT_NAMES:
        if (low.startswith(name) or low.endswith(name)) and len(words) > 1:
            return True

    # Question directed at bot
    if "?" in text and has_name:
        return True

    # 3+ words containing bot name -> likely addressing it
    if len(words) >= 3:
        return True

    return False


def is_dismiss(text: str) -> bool:
    """Return True if the message is telling the bot to stop / go away."""
    if not text:
        return False
    low = text.lower().strip()

    # Check exact dismiss phrases
    for phrase in DISMISS_PHRASES:
        if phrase in low:
            return True

    # Check pattern: dismiss + bot name
    # e.g. "ga ngomong sama lu bot idol"
    for name in BOT_NAMES:
        for phrase in DISMISS_PHRASES:
            if phrase in low and name in low:
                return True

    return False


def clean_trigger(text: str, bot_username: str = None) -> str:
    """Remove @mention from the text, keep the rest."""
    if not text:
        return ""
    result = text
    if bot_username:
        result = re.sub(
            rf"@{re.escape(bot_username)}",
            "",
            result,
            flags=re.IGNORECASE,
        )
    return result.strip()
