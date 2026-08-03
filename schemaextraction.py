from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schema import Resume
import anthropic

load_dotenv()

client = anthropic.Anthropic()

SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

def organize_resume (text, prompt):
    response = client.messages.parse(
        model = SCHEMA_EXTRACTION_MODEL,
        max_tokens = 2000,
        temperature = 0.1,
        system = prompt,
        messages=[{"role":"user", "content": text}],
        output_format = Resume,
    )
    return response.parsed_output

file_path = "sampleresume.pdf"

if __name__ == "__main__":
    raw_text = parse_pdf(file_path)
    result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
    print(result)