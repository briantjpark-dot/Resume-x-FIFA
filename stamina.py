from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume
from schema import Experience

load_dotenv()
RESUME_DIR = Path("resume_batch_stamina_40")
SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

BANDS = [
    (0,   15,  45, 62),
    (15,  38,  64, 74),
    (38,  55,  76, 87),
    (57,  99,  88, 99),
]

def correct_format(date_str):
    if not date_str:
        return None
    date_str = date_str.strip()
    for date_format in ("%m-%Y", "%m/%Y", "%Y-%m", "%B %Y", "%b %Y", "%Y"):
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue
    return None

def get_period(start_date, end_date):
    start = correct_format(start_date)
    if start is None:
        return 0

    if end_date is None:
        end = datetime.now()
    else:
        end = correct_format(end_date)
        if end is None:
            end = datetime.now()

    total_months = (end.year - start.year) * 12 + (end.month - start.month)
    return max(0, total_months)

def diminishing_sum(bucket_weights: list[int]) -> float:
    weight_sorted = sorted(bucket_weights, reverse=True)
    total = 0
    t = 0
    for weight in weight_sorted:
        total += weight * (0.7 ** t)
        t += 1
    return total

def stam_rating(raw: float) -> int:
    for lo, hi, r_lo, r_hi in BANDS:
        if lo <= raw < hi:
            frac = (raw - lo) / (hi - lo)
            return round(r_lo + frac * (r_hi - r_lo))
    return 99 if raw >= BANDS[-1][1] else BANDS[0][2]

def rate_stamina(result) -> int:
    periods = []
    for exp in result.experiences:
        start = correct_format(exp.start_date)
        if start is None:
            continue
        end = correct_format(exp.end_date)
        start_str = start.strftime("%m-%Y")
        end_str = end.strftime("%m-%Y") if end else None
        periods.append(get_period(start_str, end_str))
    stamina_total = diminishing_sum(periods)
    return stam_rating(stamina_total)

def full_stamina_rating(resume_dir):
    ratings = {}
    for pdf_path in sorted(resume_dir.glob("*.pdf")):
        raw_text = parse_pdf(str(pdf_path))
        result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
        ratings[pdf_path.name] = rate_stamina(result)
    return ratings



if __name__ == "__main__":
    results = full_stamina_rating(RESUME_DIR)
    print("\n--- Stamina Ratings ---")
    for resume_name, rating in results.items():
        print(f"{resume_name}: {rating}")