from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume

from caliber import rate_caliber
from education import rate_education
from impact import rate_impact
from leadership import rate_leadership
from stamina import rate_stamina
from technicals import rate_technical

load_dotenv()
RESUME_PATH = Path("sampleresume.pdf")
SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

LOGO_DIR = Path("school logos")
LOGO_MAP = {
    "Pomona": "Pomona_Color.svg",
    "Pitzer": "Pitzer_Color.png",
    "CMC": "CMC_Color.svg",
    "HMC": "HMC_Color.svg",
    "Scripps": "Scripps_Color.png",
    "other": "placeholder.svg",
}

def choose_logo(university: str | None) -> Path:
    return LOGO_DIR / LOGO_MAP.get(university, "placeholder.svg")

WEIGHTS = {
    "caliber":    1.0,
    "education":  1.0,
    "impact":    1.5,
    "leadership": 1.0,
    "stamina":    1.0,
    "technical": 1.5,   # light tech/finance tilt
}

#for v2 i'll make the weights of the attributes change depending on major, similar to how FIFA rates attributes for a striker differen to a CB

def attributes_pipeline(pdf_path: Path) -> dict:
    raw_text = parse_pdf(str(pdf_path))
    result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
    parsed_resume = {
        "result": result,
        "ratings": {
            "caliber": rate_caliber(result),
            "education": rate_education(result),
            "impact": rate_impact(result),
            "leadership": rate_leadership(result),
            "stamina": rate_stamina(result),
            "technical": rate_technical(result),
        },
    }
    print("Indivudal Ratings Finished")
    return parsed_resume

def raw_overall(combined_ratings):
    weighted_sum = sum(combined_ratings[k] * WEIGHTS[k] for k in WEIGHTS)
    total_weight = sum(WEIGHTS.values())
    return weighted_sum / total_weight

#Spreading function because raw overalls are clumped in the 75~85 ish range
def final_overall(raw_overall, raw_lo=64, raw_hi=86, target_lo=60, target_hi=92):
    frac = (raw_overall - raw_lo) / (raw_hi - raw_lo)
    return max(60, min(95, round(target_lo + frac * (target_hi - target_lo))))

def card_type(raw):
    base = final_overall(raw)   # caps at 92
    if raw >= 88: #beginning condition to be considered for a icon
        # map raw 88-99 onto 93-97 (the icon range)
        frac = (raw - 88) / (99 - 88)
        return round(93 + frac * (97 - 93)), "toty"
    return base, "base"

def build_card(pdf_path: Path) -> dict:
    data = attributes_pipeline(pdf_path)
    result = data["result"]
    ratings = data["ratings"]
    overall, tier = card_type(raw_overall(ratings))
    education = result.education[0] if result.education else None
    full_name = " ".join(part for part in [result.name, result.last_name] if part) or None
    return {
        "name": full_name,
        "last name": result.last_name,
        "overall": overall,
        "card_tier": tier,
        "stats": ratings,
        "university": education.university if education else None,
        "major": education.major if education else None,
        "school logo": str(choose_logo(education.university if education else None)),
    }


if __name__ == "__main__":
    if not RESUME_PATH.exists():
        print(f"\n No PDF file was found at: {RESUME_PATH.resolve()}")
    else:
        card = build_card(RESUME_PATH)
        print(f"\n {RESUME_PATH.name}")
        for field, value in card.items():
            print(f"  {field:<16}: {value}")
