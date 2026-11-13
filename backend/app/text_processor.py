MAX_TEXT_LENGTH = 10_000


def process_text_demo(text: str) -> dict[str, str | bool]:
    return {
        "result_text": text.strip(),
        "processor": "demo_echo",
        "ai_configured": False,
        "notice": (
            "Demonstration only: no AI provider is configured. "
            "The text is returned unchanged apart from trimming outer whitespace; "
            "it has not been simplified."
        ),
    }
