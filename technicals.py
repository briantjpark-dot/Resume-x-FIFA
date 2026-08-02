from pathlib import Path
from dotenv import load_dotenv
from prompts import SCHEMA_EXTRACTION_PROMPT
from parser import parse_pdf
from schemaextraction import organize_resume
from schema import Resume, Skills

load_dotenv()
SCHEMA_EXTRACTION_MODEL = "claude-sonnet-4-6"

ALIASES = {
    # --- TOP tier ---
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "cv": "computer vision",
    "nlp": "natural language processing",
    "rl": "reinforcement learning",
    "distributed computing": "distributed systems",
    "algo trading": "algorithmic trading",
    "algotrading": "algorithmic trading",
    "quant finance": "quantitative finance",
    "quantitative trading": "quantitative finance",
    "quant": "quantitative finance",
    "crypto": "cryptography",          # note: ambiguous, see caution below
    "cryptology": "cryptography",
    "web3": "blockchain",
    "solidity": "smart contracts",
    "cuda programming": "cuda",
    "gpu programming": "cuda",
    "cpp": "c++",
    "c/c++": "c++",
    "cplusplus": "c++",
    "compilers": "compiler design",
    "os": "operating systems",

    # --- MIDDLE tier ---
    "py": "python",
    "python3": "python",
    "dsa": "data structures and algorithms",
    "data structures": "data structures and algorithms",
    "algorithms": "data structures and algorithms",
    "structured query language": "sql",
    "mysql": "sql",
    "postgresql": "sql",
    "postgres": "sql",
    "psql": "sql",
    "sqlite": "sql",
    "stats": "statistics",
    "financial models": "financial modeling",
    "fin modeling": "financial modeling",
    "data eng": "data engineering",
    "data analytics": "data analysis",
    "cloud": "cloud computing",
    "amazon web services": "aws",
    "ec2": "aws",
    "s3": "aws",
    "linalg": "linear algebra",
    "apis": "api development",
    "rest api": "api development",
    "restful api": "api development",
    "api": "api development",
    "reactjs": "react",
    "react.js": "react",
    "db": "databases",
    "database": "databases",
    "version control": "git",
    "github": "git",
    "rlang": "r",

    # --- BOTTOM tier ---
    "microsoft excel": "excel",
    "ms excel": "excel",
    "spreadsheets": "excel",
    "microsoft powerpoint": "powerpoint",
    "ppt": "powerpoint",
    "microsoft word": "word",
    "ms word": "word",
    "hypertext markup language": "html",
    "html5": "html",
    "css3": "css",
    "js": "javascript",
    "ecmascript": "javascript",
    "es6": "javascript",
    "gsheets": "google sheets",
    "powerbi": "power bi",
    "microsoft power bi": "power bi",
}

TOP = {
    "linux",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "computer vision",
    "natural language processing",
    "reinforcement learning",
    "distributed systems",
    "algorithmic trading",
    "quantitative finance",
    "financial engineering",
    "cryptography",
    "blockchain",
    "smart contracts",
    "embedded systems",
    "cuda",
    "c++",
    "compiler design",
    "operating systems"
}

MIDDLE = {
    "python",
    "javascript",
    "java",
    "c",
    "data structures and algorithms",
    "sql",
    "statistics",
    "econometrics",
    "financial modeling",
    "data engineering",
    "data analysis",
    "cloud computing",
    "aws",
    "linear algebra",
    "api development",
    "react",
    "databases",
    "git",
    "r"
}

BOTTOM = {
    "excel",
    "powerpoint",
    "html",
    "css",
    "word",
    "google sheets",
    "tableau",
    "power bi",
    "canva"
}

BANDS = [
    (0,   9,   60, 72), 
    (9,   13,  73, 78),
    (13,  18,  82, 90),
    (18,  22,  88, 99),
]

#Using the same weight, sum, and band logic from leadership -> these functions are redundant but i 
# wanna make each rating be individually tested so they can be changed later if needed
def normalize(skill: str) -> str:
    s = skill.strip().lower()
    return ALIASES.get(s, s)

def technical_weight(bucket: str) -> int:
    if bucket in TOP:
        return 10
    if bucket in MIDDLE:
            return 5
    if bucket in BOTTOM:
            return 2
    return 0

def diminishing_sum(bucket_weights: list[int]) -> float:
    weight_sorted = sorted(bucket_weights, reverse=True)
    total = 0
    t = 0
    for weight in weight_sorted:
        total += weight * (0.5 ** t)
        t += 1
    return total

def tech_rating(raw: float) -> int:
    for lo, hi, r_lo, r_hi in BANDS:
        if lo <= raw < hi:
            frac = (raw - lo) / (hi - lo)
            return round(r_lo + frac * (r_hi - r_lo))
    return 99 if raw >= BANDS[-1][1] else BANDS[0][2]

RESUME_DIR = Path("resume_batch_tech_40")

if __name__ == "__main__":
    for pdf_path in sorted(RESUME_DIR.glob("*.pdf")):
        raw_text = parse_pdf(str(pdf_path))
        result = organize_resume(raw_text, SCHEMA_EXTRACTION_PROMPT)
        skills = result.skills if result.skills else Skills()
        normalized_skills = [normalize(skill) for skill in skills.technical_skills]
        technical_weighted = [technical_weight(skill) for skill in normalized_skills]
        technical_weighted_total = diminishing_sum(technical_weighted)
        technical_rating = tech_rating(technical_weighted_total)
        print(f"{pdf_path.name}: rating={technical_rating}")
