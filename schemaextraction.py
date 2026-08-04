from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schema import Resume
import anthropic

load_dotenv()

client = anthropic.Anthropic()

SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

def organize_resume (text, prompt):
    response = client.messages.create(
        model = SCHEMA_EXTRACTION_MODEL,
        max_tokens = 2000,
        temperature = 0.1,
        system = prompt,
        messages=[{"role":"user", "content": text}],
    )
    raw_json = response.content[0].text.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.strip("`")
        raw_json = raw_json.removeprefix("json").strip()
    return Resume.model_validate_json(raw_json)

file_path = "sampleresume.pdf"

if __name__ == "__main__":
    raw_text = parse_pdf(file_path)
    result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
    print(result)