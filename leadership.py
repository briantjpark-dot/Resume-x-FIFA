from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume
from schema import Resume

load_dotenv()
RESUME_DIR = Path("resume_batch_40")
SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"


#Going to implement scope on V2, just titles for now


TOP = {
    "founder",
    "president",
    "captain",
    "editor_in_chief",
    "chief executive officer",
    "chief financial officer"
}

MIDDLE = {
    "director",
    "vice_president",
    "chair",
    "treasurer",
    "secretary",
    "project manager"
    "officer",
    "portfolio manager",
    "senior analyst",
    "editor"
} 

LOW = {
    "team_lead",
    "manager",
    "resident_advisor",
    "teaching_assistant",
}

BOTTOM = {
    "member"
}

BANDS = [
    (0.0,  2.5,  45, 62),   # non-leader (low + minimal merged)
    (2.5,  5.5,  64, 74),
    (5.5,  9.0,  76, 87),
    (9.0, 16.0,  86, 99),   # high leader
]

#Not even specing, so that top positions really stand out

def bucket_weight(bucket: str) -> int:
    if bucket in TOP:
        return 10
    if bucket in MIDDLE:
        return 5
    if bucket in LOW:
        return 2
    if bucket in BOTTOM:
        return 1
    return 0


def diminishing_sum(bucket_weights: list[int]) -> float:
    weight_sorted = sorted(bucket_weights, reverse=True)
    total = 0
    t = 0
    for weight in weight_sorted:
        total += weight * (0.65 ** t)
        t += 1
    return total

def lea_rating(raw: float) -> int:
    for lo, hi, r_lo, r_hi in BANDS:
        if lo <= raw < hi:
            frac = (raw - lo) / (hi - lo)
            return round(r_lo + frac * (r_hi - r_lo))
    return 99 if raw >= BANDS[-1][1] else BANDS[0][2]

def rate_leadership(result) -> int:
    leadership_buckets = [exp.leadership_bucket for exp in result.experiences]
    leadership_weighted = [bucket_weight(bucket) for bucket in leadership_buckets]
    leadership_weighted_total = diminishing_sum(leadership_weighted)
    return lea_rating(leadership_weighted_total)

def full_leadership_rating(resume_dir):
    ratings = {}
    for pdf_path in sorted(resume_dir.glob("*.pdf")):
        raw_text = parse_pdf(str(pdf_path))
        result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
        ratings[pdf_path.name] = rate_leadership(result)
    return ratings


if __name__ == "__main__":
    results = full_leadership_rating(RESUME_DIR)
    print("\n--- Leadership Ratings ---")
    for resume_name, rating in results.items():
        print(f"{resume_name}: {rating}")