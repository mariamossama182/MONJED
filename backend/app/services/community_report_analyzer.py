from google import genai
from dotenv import load_dotenv

from app.schemas.community_report import (
    CommunityReportInput,
    CommunityReportAnalysis,
)


load_dotenv()

client = genai.Client()


def analyze_community_report(
    report: CommunityReportInput
) -> CommunityReportAnalysis:

    prompt = f"""
You are the community-report analysis component of MONJED,
a disaster decision-support system.

Analyze the following community report.

Location:
{report.location}

Report:
{report.report_text}

Extract only information supported by the report.

Rules:
- Do not invent information.
- If the hazard is clearly a flood, classify it as "flood".
- Otherwise use "unknown".
- If something is not mentioned or cannot be inferred safely, use false.
- Severity must be based only on the report content.
- extracted_evidence must contain short factual statements supported by the report.
- mobility_assistance_needed should be true when someone may be physically unable to carry out an evacuation or safety action.
- help_needed should be true when the report indicates that assistance is needed or people cannot safely act without help.
- transportation_needed must be true ONLY when the report explicitly mentions needing transportation, a vehicle, a ride, or lack of transport.
- Do not set transportation_needed to true only because someone has limited mobility.
- mobility_assistance_needed and transportation_needed are separate concepts.
- Never infer a need that is not directly supported by the report.

"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": CommunityReportAnalysis.model_json_schema(),
        },
    )

    return CommunityReportAnalysis.model_validate_json(
        interaction.output_text
    )