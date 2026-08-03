from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume
import re

load_dotenv()
RESUME_DIR = Path("resume_batch_impact_40")
SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

CAP = 8

BANDS = [
    (0,  1,  45, 62),
    (1,  3,  64, 74),
    (3,  5,  76, 87),
    (5,  11,  88, 99),
]

# the amazing thing is that each bullet is already it's own individual string

_IMPACT = re.compile(r"""
      \d\s?% #for percentages
    | \$\s?\d  #dollars
    | \d\s?[xX]\b #multiples
    | \d\+ #growth
    | \d\s?(?:[KkMm]|million|thousand|billion)\b #larger values esp for finance
""", re.VERBOSE)

def is_quantified(bullet: str) -> bool:
    return bool(bullet) and bool(_IMPACT.search(bullet))

def impact_raw(resume):
    count = 0
    for exp in resume.experiences:
        for bullet in exp.bullets:
            if is_quantified(bullet):
                count += 1
    return count, min(count, CAP)

def imp_rating(raw: float) -> int:
    for lo, hi, r_lo, r_hi in BANDS:
        if lo <= raw < hi:
            frac = (raw - lo) / (hi - lo)
            return round(r_lo + frac * (r_hi - r_lo))
    return 99 if raw >= BANDS[-1][1] else BANDS[0][2]

def rate_impact(result) -> int:
    count, raw_impact = impact_raw(result)
    return imp_rating(raw_impact)

def full_impact_rating(resume_dir):
    ratings = {}
    for pdf_path in sorted(resume_dir.glob("*.pdf")):
        raw_text = parse_pdf(str(pdf_path))
        result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
        ratings[pdf_path.name] = rate_impact(result)
    return ratings

#V2 will include an additional layer with LLM-based nuances
#Currently there will be dead spots 61–65, 71–75, or 81–85

if __name__ == "__main__":
    results = full_impact_rating(RESUME_DIR)
    print("\n--- Impact Ratings ---")
    for resume_name, rating in results.items():
        print(f"{resume_name}: {rating}")
    