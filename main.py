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

