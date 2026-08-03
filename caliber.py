from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume

load_dotenv()
RESUME_DIR = Path("resume_batch_caliber_40")
SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

TOP = {
    "internship",
    "fellowship",
    "research"
}

MIDDLE = {
    "work",
    "project",
} 

BOTTOM = {
    "club",
    "volunteer"
}

BANDS = [
    (0,   6,   60, 66),
    (6,   12,  68, 78),
    (12,  16,  80, 86),
    (16,  24,  88, 99),
]

def bucket_weight(experience_type: str) -> int:
    if experience_type in TOP:
        return 10
    if experience_type in MIDDLE:
        return 5
    if experience_type in BOTTOM:
        return 2
    return 0


def diminishing_sum(weights: list[float], decay: float = 0.65) -> float:
    total = 0
    for t, weight in enumerate(sorted(weights, reverse=True)):
        total += weight * (decay ** t)
    return total

def cal_rating(raw: float) -> int:
    for lo, hi, r_lo, r_hi in BANDS:
        if lo <= raw < hi:
            frac = (raw - lo) / (hi - lo)
            return round(r_lo + frac * (r_hi - r_lo))
    return 99 if raw >= BANDS[-1][1] else BANDS[0][2]

def full_caliber_rating():
    ratings = {}
    for pdf_path in sorted(RESUME_DIR.glob("*.pdf")):
        raw_text = parse_pdf(str(pdf_path))
        result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
        experience_types = [exp.type for exp in result.experiences]
        type_weighted = [bucket_weight(experience_type) for experience_type in experience_types]
        caliber_weighted_total = diminishing_sum(type_weighted)
        ratings[pdf_path.name] = cal_rating(caliber_weighted_total)
    return ratings


if __name__ == "__main__":
    results = full_caliber_rating()
    print("\n--- Caliber Ratings ---")
    for resume_name, rating in results.items():
        print(f"{resume_name}: {rating}")
