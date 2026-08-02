from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume
from schema import Resume, Education
import math

load_dotenv()

SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"
HONORS_KEYWORDS = [
    "dean", "cum laude", "magna", "summa",
    "phi beta kappa", "honor society", "honors program", "honors college",
    "scholar", "valedictorian", "salutatorian", "distinction", "merit", "goldwater", 
    "tau beta pi", "sigma xi", "putnam", "regeneron"
]
PER_HONOR = 0.02 #2% per honor
MAX_HONORS = 3 # max 9% for honors boost

#going to use a sigmoid curve
#c = 3.3, the average gpa at the 5Cs
#k = 2.5?

def raw_gpa_score(gpa: float) -> float:
    rating = 60 + 39 * (1 / (1 + math.exp(-2.5 * (gpa - 3.3))))
    return rating

def honors_multiplier(honors: list[str]) -> float:
    count = 0
    for h in honors:
        if any(kw in h.lower() for kw in HONORS_KEYWORDS):
            count += 1
    return 1.0 + PER_HONOR * min(count, MAX_HONORS)

def rating(edu):
    base = raw_gpa_score(edu.gpa) if edu.gpa is not None else 75.0
    return round(min(99, base * honors_multiplier(edu.honors)))

RESUME_DIR = Path("resume_batch_edu_40")

if __name__ == "__main__":
    for pdf_path in sorted(RESUME_DIR.glob("*.pdf")):
        raw_text = parse_pdf(str(pdf_path))
        result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
        edu = result.education[0] if result.education else Education()
        gpa_score = raw_gpa_score(edu.gpa) if edu.gpa is not None else 75.0
        multiplier = honors_multiplier(edu.honors)
        education_rating = rating(edu)
        print(f"{pdf_path.name}: gpa_score={gpa_score}, honors_multiplier={multiplier}, rating={education_rating}")