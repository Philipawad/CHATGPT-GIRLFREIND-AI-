"""Axel Stålhammar – skattejurist i terminalen, byggd på Claude API.

Kör:  python app.py
Kräver: ANTHROPIC_API_KEY (eller en `ant auth login`-profil).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import anthropic

# Sökvägar relativt den här filen, så att appen går att köra från valfri mapp
BASE_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT_FILE = BASE_DIR / "system_prompt.md"
MEMORY_FILE = BASE_DIR / "minne.json"

# Modellen går att byta via miljövariabel utan att röra koden
MODEL = os.environ.get("SKATTEJURIST_MODEL", "claude-opus-5")

# Hur många tidigare meddelanden som följer med från disk vid omstart
MEMORY_LIMIT = 40

# Webbsökning begränsad till primärkällor, så att Axel kan verifiera
# aktuell lagtext, belopp och praxis i stället för att gissa
WEB_SEARCH_TOOL = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 5,
    "allowed_domains": [
        "riksdagen.se",
        "skatteverket.se",
        "domstol.se",
        "lagen.nu",
        "regeringen.se",
        "hudoc.echr.coe.int",
    ],
}

# Max antal gånger vi återupptar en pausad sökrunda (pause_turn) per fråga
MAX_CONTINUATIONS = 5


def load_memory() -> list[dict]:
    """Läser tidigare konversation (endast text) från disk."""
    if not MEMORY_FILE.exists():
        return []
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    history = data[-MEMORY_LIMIT:]
    # API:t kräver att första meddelandet kommer från användaren
    while history and history[0]["role"] != "user":
        history.pop(0)
    return history


def save_memory(text_log: list[dict]) -> None:
    """Sparar konversationen som ren text så att den överlever omstart."""
    MEMORY_FILE.write_text(
        json.dumps(text_log[-MEMORY_LIMIT:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def ask_axel(
    client: anthropic.Anthropic, system: str, messages: list
) -> tuple[str, list]:
    """Skickar konversationen till Claude, streamar svaret och returnerar
    (svarstext, nya meddelanden att lägga till i historiken)."""
    new_messages: list = []
    text_parts: list[str] = []

    for _ in range(MAX_CONTINUATIONS + 1):
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=[
                {
                    "type": "text",
                    "text": system,
                    # System-prompten är stabil och cachas därför
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=messages + new_messages,
            tools=[WEB_SEARCH_TOOL],
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            # Om modellen skulle vägra en fråga körs den om på en
            # reservmodell på serversidan i stället för att bara avbrytas
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
            response = stream.get_final_message()

        # Hela innehållet (inkl. sökresultat) sparas i historiken
        new_messages.append({"role": "assistant", "content": response.content})
        text_parts.extend(b.text for b in response.content if b.type == "text")

        if response.stop_reason == "refusal":
            print("\n[Frågan avböjdes av modellen. Formulera om den.]")
            break
        if response.stop_reason != "pause_turn":
            break
        # pause_turn: en lång sökrunda pausades, skicka tillbaka för att fortsätta

    print()
    return "".join(text_parts), new_messages


def main() -> None:
    system = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    client = anthropic.Anthropic()

    # messages = full historik för API:t, text_log = det som sparas på disk
    text_log = load_memory()
    messages: list = [dict(m) for m in text_log]

    print("=" * 60)
    print(" AXEL STÅLHAMMAR – skattejurist")
    print(" Beskriv ditt ärende. Skriv 'rensa' för att nollställa minnet,")
    print(" 'avsluta' för att gå.")
    print("=" * 60)
    if text_log:
        print(f"(Minne laddat: {len(text_log)} tidigare meddelanden)\n")

    while True:
        try:
            user_input = input("\nDu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in {"avsluta", "exit", "quit"}:
            break
        if user_input.lower() == "rensa":
            text_log.clear()
            messages.clear()
            save_memory(text_log)
            print("Minnet är rensat.")
            continue

        messages.append({"role": "user", "content": user_input})
        print("\nAxel: ", end="", flush=True)

        try:
            answer, new_messages = ask_axel(client, system, messages)
        except anthropic.AuthenticationError:
            print("\nOgiltig API-nyckel. Sätt ANTHROPIC_API_KEY.")
            messages.pop()
            continue
        except anthropic.RateLimitError:
            print("\nFör många anrop just nu. Vänta en stund och försök igen.")
            messages.pop()
            continue
        except anthropic.APIStatusError as e:
            print(f"\nAPI-fel ({e.status_code}): {e.message}")
            messages.pop()
            continue
        except anthropic.APIConnectionError:
            print("\nIngen kontakt med API:t. Kontrollera nätverket.")
            messages.pop()
            continue

        messages.extend(new_messages)
        text_log.append({"role": "user", "content": user_input})
        text_log.append({"role": "assistant", "content": answer})
        save_memory(text_log)


if __name__ == "__main__":
    main()
