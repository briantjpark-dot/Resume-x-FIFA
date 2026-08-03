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
RESUME_DIR = Path("testresumes") #get claude to generate full tings here
SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

WEIGHTS = {
    "caliber":    1.0,
    "education":  1.0,
    "impact":    1.5,
    "leadership": 1.0,
    "stamina":    1.0,
    "technical": 1.5,   # light tech/finance tilt
}

#for v2 i'll make the weights of the attributes change depending on major, similar to how FIFA rates attributes for a striker differen to a CB

def run_full_pipeline(resume_dir: Path) -> dict:
    combined_ratings = {}
    for pdf_path in sorted(resume_dir.glob("*.pdf")):
        raw_text = parse_pdf(str(pdf_path))
        result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
        combined_ratings[pdf_path.name] = {
            "caliber": rate_caliber(result),
            "education": rate_education(result),
            "impact": rate_impact(result),
            "leadership": rate_leadership(result),
            "stamina": rate_stamina(result),
            "technical": rate_technical(result),
        }
    print("Indivudal Ratings Finished")
    return combined_ratings

def raw_overall(combined_ratings):
    weighted_sum = sum(combined_ratings[k] * WEIGHTS[k] for k in WEIGHTS)
    total_weight = sum(WEIGHTS.values())
    return weighted_sum / total_weight

#Spreading function because raw overalls are clumped in the 75~85 ish range
def stretch(raw_overall, raw_lo=64, raw_hi=86, target_lo=60, target_hi=92):
    frac = (raw_overall - raw_lo) / (raw_hi - raw_lo)
    return max(60, min(95, round(target_lo + frac * (target_hi - target_lo))))

def final_overall(raw):
    base = stretch(raw)   # caps at 92
    if raw >= 88: #beginning condition to be considered for a toty
        # map raw 88-99 onto 93-95 (the toty range)
        frac = (raw - 88) / (99 - 88)
        return round(93 + frac * (95 - 93)), "toty"
    return base, "base"


if __name__ == "__main__":
    final_results = run_full_pipeline(RESUME_DIR)

    if not final_results:
        print(f"\n No PDF files were found in: {RESUME_DIR.resolve()}")
    else:
        print("\n=== FULL PIPELINE RESULTS ===")
        for filename, profile in final_results.items():
            print(f"\n {filename}")
            for category, rating in profile.items():
                print(f"  {category:<12}: {rating}")
            raw = raw_overall(profile)
            print(f"  {'raw overall':<12}: {raw}")
            print(f"  {'overall':<12}: {stretch(raw)}")

