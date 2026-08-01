"""Generate 40 IMPACT-labeled college resumes to validate the Impact stat.

IMPACT is the CONTROLLED axis: number of quantified achievements is set per tier.
  high    : 5-8 quantified bullets
  mid     : 3-4 quantified bullets
  low     : 1-2 quantified bullets
  minimal : 0 quantified bullets (all vague duties)

Other stats (leadership, prestige) are RANDOMIZED so they don't confound impact.

Two deliberate stress-tests baked in:
  1. TRAP bullets (dates, team sizes, GPA, durations) sprinkled in — must NOT be
     counted by is_quantified. The manifest says which resumes carry traps.
  2. Magnitude variety — some quantified bullets are huge ($500K, 80%), some tiny
     ($50, 5%). Deterministic counts them equally; useful for testing a future
     LLM magnitude layer. Manifest records planted count so you have an answer key.

Output:
  batch_impact/resume_##_IMPACT-<tier>.pdf
  batch_impact/manifest.csv   (file, intended_impact, planted_quantified, has_traps)
"""
import csv, os, random
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.colors import HexColor

random.seed(7)
OUT = "/home/claude/batch_impact"
os.makedirs(OUT, exist_ok=True)

def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=17, alignment=TA_CENTER, spaceAfter=2))
    s.add(ParagraphStyle("MyContact", fontName="Helvetica", fontSize=9, alignment=TA_CENTER, textColor=HexColor("#444"), spaceAfter=8))
    s.add(ParagraphStyle("Sec", fontName="Helvetica-Bold", fontSize=11, textColor=HexColor("#1a1a1a"), spaceBefore=8, spaceAfter=3))
    s.add(ParagraphStyle("RoleHead", fontName="Helvetica-Bold", fontSize=10, spaceAfter=1))
    s.add(ParagraphStyle("Sub", fontName="Helvetica-Oblique", fontSize=9, textColor=HexColor("#333"), spaceAfter=2))
    s.add(ParagraphStyle("MyBullet", fontName="Helvetica", fontSize=9.3, leftIndent=14, spaceAfter=1.5, leading=12))
    s.add(ParagraphStyle("MyBody", fontName="Helvetica", fontSize=9.3, spaceAfter=2, leading=12))
    return s

def build(path, name, contact, sections):
    S = styles()
    doc = SimpleDocTemplate(path, pagesize=letter, topMargin=0.55*inch, bottomMargin=0.55*inch,
                            leftMargin=0.7*inch, rightMargin=0.7*inch)
    story = [Paragraph(name, S["Name"]), Paragraph(contact, S["MyContact"])]
    for title, blocks in sections:
        if not blocks: continue
        story.append(Paragraph(title.upper(), S["Sec"]))
        story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#888"), spaceBefore=0, spaceAfter=4))
        for b in blocks:
            if b["kind"] == "role":
                story.append(Paragraph(b["head"], S["RoleHead"]))
                if b.get("sub"): story.append(Paragraph(b["sub"], S["Sub"]))
                for x in b.get("bullets", []): story.append(Paragraph("&bull;&nbsp;&nbsp;" + x, S["MyBullet"]))
                story.append(Spacer(1, 3))
            else:
                story.append(Paragraph(b["text"], S["MyBody"]))
    doc.build(story)

FIRST = ["Jordan","Taylor","Sam","Alex","Morgan","Riley","Casey","Jamie","Avery","Quinn","Drew","Reese","Cameron","Devon","Hayden","Rowan","Parker","Sage","Blake","Elliot","Harper","Logan","Micah","Peyton","River","Noa","Kai","Remy","Sky","Lane"]
LAST = ["Chen","Morgan","Rivera","Patel","Kim","Nguyen","Garcia","Okafor","Silva","Cohen","Ali","Brooks","Diaz","Ford","Gupta","Ito","Jones","Kaur","Lopez","Park","Reyes","Singh","Tran","Vargas","Wong","Bauer","Costa","Dell","Ekwueme","Frost"]
SCHOOLS = ["University of Michigan","Stanford University","Arizona State University","Ohio State University","Community College of Denver","UC Berkeley","University of Texas","Boston University"]
MAJORS = ["Computer Science","Business Administration","Economics","Marketing","Data Science","Mechanical Engineering","Communications","Finance"]
ORGS = ["Robotics Club","Marketing Association","Investment Club","Volunteer Corps","Coding Club","Student Government","Debate Team","Environmental Alliance","Local Startup","Campus Newspaper","Research Lab","Retail Co."]
LEAD_TITLES = ["President","Vice President","Treasurer","Team Lead","Member","Volunteer","Intern","Coordinator","Analyst","Committee Member"]

# HIGH-magnitude quantified bullets (big numbers)
Q_HIGH = [
    "Increased revenue by 80% over two quarters",
    "Raised $500,000 in sponsorship funding",
    "Grew the user base to 1M+ active accounts",
    "Cut operating costs by $250,000 annually",
    "Improved processing speed by 10x",
    "Scaled the program to 5,000+ participants",
    "Boosted engagement 95% year over year",
    "Managed a $2 million event budget",
]
# LOW-magnitude quantified bullets (small numbers — still count deterministically)
Q_LOW = [
    "Increased signups by 5%",
    "Raised $50 at the bake sale",
    "Grew the group to 20+ members",
    "Reduced errors by 8%",
    "Reached 30 downloads in the first week",
    "Improved turnout by 12%",
    "Saved roughly $200 on supplies",
    "Handled 15+ tickets per shift",
]
VAGUE = [
    "Responsible for managing social media accounts",
    "Helped organize weekly meetings and events",
    "Assisted members with questions and tasks",
    "Contributed to group projects and discussions",
    "Attended events and took detailed notes",
    "Supported the team during busy periods",
    "Coordinated with staff on various initiatives",
    "Participated in outreach and planning",
    "Maintained records and updated documents",
    "Collaborated with peers on assignments",
]
# TRAP bullets: contain numbers that must NOT be counted as impact
TRAPS = [
    "Led a team of 4 on the capstone project",
    "Worked from 2023-2024 in the department",
    "Volunteered for 3 years at the shelter",
    "Maintained a 3.8 GPA while working part-time",
    "Completed CS 101 and MATH 204 coursework",
    "Coordinated a group of 6 volunteers",
    "Served 2 semesters on the committee",
]

def make_bullets(tier, use_traps):
    """Return (bullets, planted_quantified_count)."""
    n_q = {"high": random.randint(5,8), "mid": random.randint(3,4),
           "low": random.randint(1,2), "minimal": 0}[tier]
    # mix magnitudes so future LLM layer has something to differentiate
    q = random.sample(Q_HIGH, min(n_q, len(Q_HIGH))) if random.random()<0.5 else random.sample(Q_LOW, min(n_q, len(Q_LOW)))
    if n_q > len(q):  # need more, pull from the other pool
        q += random.sample([b for b in Q_HIGH+Q_LOW if b not in q], n_q-len(q))
    vague = random.sample(VAGUE, random.randint(2,4))
    traps = random.sample(TRAPS, random.randint(1,2)) if use_traps else []
    bullets = q + vague + traps
    random.shuffle(bullets)
    return bullets, n_q

def make_resume(idx, tier):
    name = f"{random.choice(FIRST)} {random.choice(LAST)}"
    contact = f"{name.lower().replace(' ','.')}@email.com  |  (555) {random.randint(100,999)}-{random.randint(1000,9999)}"
    use_traps = random.random() < 0.6
    all_bullets, planted = make_bullets(tier, use_traps)

    # split bullets across 2-3 experiences (impact is resume-wide, so distribution doesn't matter)
    random.shuffle(all_bullets)
    n_exp = random.randint(2,3)
    chunks = [all_bullets[i::n_exp] for i in range(n_exp)]
    exps = []
    for c in chunks:
        if not c: continue
        exps.append({"kind":"role",
                     "head":f"{random.choice(LEAD_TITLES)} &mdash; {random.choice(ORGS)}",
                     "sub":f"{random.choice(['01','06','09'])}/{random.choice([2023,2024])} &ndash; {random.choice(['Present','05/2025','08/2024'])}",
                     "bullets":c})

    edu = [{"kind":"role","head":random.choice(SCHOOLS),
            "sub":f"B.S. in {random.choice(MAJORS)}  |  Expected {random.choice([2026,2027])}"
                  + (f"  |  GPA: {round(random.uniform(3.0,4.0),2)}/4.00" if random.random()<0.7 else "")}]

    sections = [("Education",edu),("Experience",exps),
                ("Skills",[{"kind":"body","text":"<b>Skills:</b> Python, Excel, JavaScript, SQL"}])]

    fname = f"resume_{idx:02d}_IMPACT-{tier}.pdf"
    build(os.path.join(OUT,fname), name, contact, sections)
    return {"file":fname,"intended_impact":tier,"planted_quantified":planted,"has_traps":use_traps}

plan = (["high"]*10 + ["mid"]*10 + ["low"]*10 + ["minimal"]*10)
random.shuffle(plan)
rows = [make_resume(i+1, t) for i, t in enumerate(plan)]

with open(os.path.join(OUT,"manifest.csv"),"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["file","intended_impact","planted_quantified","has_traps"])
    w.writeheader(); w.writerows(sorted(rows, key=lambda r:r["file"]))

from collections import Counter
print(f"Generated {len(rows)} impact-labeled resumes")
print("Impact tiers:", dict(Counter(r["intended_impact"] for r in rows)))
print("With traps:", sum(r["has_traps"] for r in rows), "of 40")
