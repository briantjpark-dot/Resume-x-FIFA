from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume

from caliber import full_caliber_rating
from education import full_education_rating
from impact import full_impact_rating
from leadership import full_leadership_rating
from stamina import full_stamina_rating
from technicals import full_technical_rating
import re

load_dotenv()
RESUME_DIR = Path("") #get claude to generate full tings here
SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

def run_full_pipeline(resume_dir: Path) -> dict:
    caliber_results = full_caliber_rating(resume_dir)
    education_results = full_education_rating(resume_dir)
    impact_results = full_impact_rating(resume_dir)
    leadership_results = full_leadership_rating(resume_dir)
    stamina_results = full_stamina_rating(resume_dir)
    technical_results = full_technical_rating(resume_dir)

    combined_ratings = {}
    for pdf_path in sorted(resume_dir.glob("*.pdf")):
        filename = pdf_path.name
        combined_ratings[filename] = {
            "caliber": caliber_results.get(filename),
            "education": education_results.get(filename),
            "impact": impact_results.get(filename),
            "leadership": leadership_results.get(filename),
            "stamina": stamina_results.get(filename),
            "technical": technical_results.get(filename),
        }
    print("Indivudal Ratings Finished")
    return combined_ratings


if __name__ == "__main__":
    final_results = run_full_pipeline(RESUME_DIR)
    # Inspect/Print output for a quick check
    for filename, profile in final_results.items():
        print(filename, profile)

