# Axel Stålhammar – skattejurist

En AI-persona som går hårt mot Skatteverket och hjälper privatpersoner och ägare av små bolag med revision, omprövning, efterbeskattning, skönsbeskattning, skattetillägg, betalningssäkring och misstanke om skattebrott. Axel arbetar offensivt med tidsfrister, bevisbörda, procedurfel och den skatteplanering som lagen tillåter. Han vägrar allt som är skattebrott, eftersom det förlorar mål och leder till fängelse.

## Filer

| Fil | Innehåll |
|---|---|
| `system_prompt.md` | Själva personan. Den kan också klistras in som instruktion i ett Claude-projekt eller en custom GPT. |
| `app.py` | Chatt i terminalen via Claude API, med webbsökning mot primärkällor och lokalt minne |
| `minne.json` | Skapas automatiskt och innehåller konversationshistoriken |

## Kom igång

```bash
cd skattejurist
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python app.py
```

Byt modell med `SKATTEJURIST_MODEL`, till exempel `export SKATTEJURIST_MODEL=claude-sonnet-5`.

## Viktigt

Axel är ett beslutsstöd, inget ombud. Han skriver utkast till yttranden och överklaganden och räknar ut frister. Kontrollera ändå alltid fristerna mot ditt eget beslut. Vid misstanke om brott eller stora belopp ska en advokat föra din talan.
