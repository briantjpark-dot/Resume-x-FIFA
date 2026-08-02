from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional

LeadershipBucket = Literal[
    # founder / top-of-org
    "founder",
    "president",
    "captain",
    "editor_in_chief",
    "chief executive officer",
    "chief financial officer",
    # senior officers
    "director",
    "vice_president",
    "chair",
    "treasurer",
    "secretary",
    "officer",
    "portfolio manager",
    "senior analyst",
    "editor",
    # people / workstream leads (no formal officer title) + default / non-leadership like a participant
    "team_lead",
    "manager",
    "resident_advisor",
    "teaching_assistant",
    "member",
    "analyst",
    "consultant",
    "intern",
    "research assistant"
]


#im assuming some languages and technicals will be weighted harder than others

#make the university a literal list with other as a choice for non 5Cs

class Education(BaseModel):
    university: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None #not used for v1 calculations
    courseload: list[str] = Field(default_factory=list) #not used for v1 calculations
    gpa: Optional[float] = None
    honors: list[str] = Field(default_factory=list) #counted as a bonus

class Skills(BaseModel):
    languages: list[str] = Field(default_factory=list) 
    technical_skills: list[str] = Field(default_factory=list) #not going to touch for v1, maybe a small boost to overall rating

#Project folds into experiences
class Experience(BaseModel):
    title: Optional[str] = None
    leadership_bucket: Optional[LeadershipBucket] = None
    organization: Optional[str] = None
    type: Optional[Literal["work", "club", "research", "project", "volunteer"]] = None
    start_date: Optional[str] = None      # MM-YYYY
    end_date: Optional[str] = None        # None means ongoing, so if end_date = None, then we use datetitme and current date
    bullets: list[str] = Field(default_factory=list)

class Resume(BaseModel):
    education: list[Education] = Field(default_factory=list)
    skills: Optional[Skills] = None
    experiences: list[Experience] = Field(default_factory=list)
    awards: list[str] = Field(default_factory=list)


#ive left experience and projects out as a class because im still not sure how we are going to find 
#multiple experiences --> perhaps with just better prompting?

