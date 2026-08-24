from pydantic import BaseModel

from app.schemas.risk import RiskAssessment
from app.schemas.decision import FinalDecision
from app.schemas.accessibility import AccessibleActionPlan
from app.schemas.assistance import AssistanceRequestRecord


class MonjedAssessment(BaseModel):
    risk: RiskAssessment

    decision: FinalDecision

    accessible_action: AccessibleActionPlan | None = None

    assistance_request: AssistanceRequestRecord | None = None

    ai_alert: dict | None = None