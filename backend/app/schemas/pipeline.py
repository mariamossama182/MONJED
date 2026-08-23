from pydantic import BaseModel

from app.schemas.risk import RiskAssessment
from app.schemas.decision import FinalDecision
from app.schemas.accessibility import AccessibleActionPlan


class MonjedAssessment(BaseModel):
    risk: RiskAssessment
    decision: FinalDecision
    accessible_action: AccessibleActionPlan | None = None