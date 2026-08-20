from openai import OpenAI

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


SUMMARY_PROMPT = """Sos un asistente experto en resumir videos de YouTube de forma clara y estructurada.
Respondé siempre en el mismo idioma que la transcripción.
No inventés información que no esté en el texto."""

USER_PROMPT = """Resumí el siguiente video en este formato exacto:

**Tema principal**
[1-2 oraciones]

**Puntos clave**
• [punto 1]
• [punto 2]
• [punto 3]
• [punto 4 si aplica]
• [punto 5 si aplica]

**Conclusión**
[1-2 oraciones]

TRANSCRIPCIÓN:
{transcript}"""


def summarize(transcript: str) -> str:
    # Truncate to ~6000 words to stay within token limits
    words = transcript.split()
    if len(words) > 6000:
        transcript = " ".join(words[:6000])

    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(transcript=transcript)},
        ],
        max_tokens=1024,
        temperature=0.3,
    )
    return response.choices[0].message.content
