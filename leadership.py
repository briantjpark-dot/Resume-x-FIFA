from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume
from schema import Resume

load_dotenv()


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
    "officer",
    "portfolio manager",
    "senior analyst",
    "editor"
} 

BOTTOM = {
    "team_lead",
    "manager",
    "resident_advisor",
    "teaching_assistant",
    "member",
    "analyst",
    "consultant",
    "intern",
    "research assistant"
}

BANDS = [
    (0.0,  2.5,  60, 67),   # non-leader (low + minimal merged)
    (2.5,  9.0,  70, 83),   # mid leader
    (9.0, 16.0,  86, 99),   # high leader
]

#Not even specing, so that top positions really stand out

def bucket_weight(bucket: str) -> int:
    if bucket in TOP:
        return 10
    if bucket in MIDDLE:
            return 5
    if bucket in BOTTOM:
            return 1
    return 1


def diminishing_sum(bucket_weights: list[int]) -> float:
    weight_sorted = sorted(bucket_weights, reverse=True)
    total = 0
    t = 0
    for weight in weight_sorted:
        total += weight * (0.5 ** t)
        t += 1
    return total

def lea_rating(raw: float) -> int:
    for lo, hi, r_lo, r_hi in BANDS:
        if lo <= raw < hi:
            frac = (raw - lo) / (hi - lo)
            return round(r_lo + frac * (r_hi - r_lo))
    return 99 if raw >= BANDS[-1][1] else BANDS[0][2]



RESUME_DIR = Path("resume_batch_40")

if __name__ == "__main__":
    for pdf_path in sorted(RESUME_DIR.glob("*.pdf")):
        raw_text = parse_pdf(str(pdf_path))
        result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
        leadership_buckets = [exp.leadership_bucket for exp in result.experiences]
        leadership_weighted = [bucket_weight(bucket) for bucket in leadership_buckets]
        leadership_weighted_total = diminishing_sum(leadership_weighted)
        leadership_rating = lea_rating(leadership_weighted_total)
        print(f"{pdf_path.name}: score={leadership_weighted_total:.2f} rating={leadership_rating}")


