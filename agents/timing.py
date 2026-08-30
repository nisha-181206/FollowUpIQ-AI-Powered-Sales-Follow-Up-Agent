from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
import json


client = Groq(api_key=GROQ_API_KEY)


def determine_followup_timing(
    conversation,
    analysis,
    lead_score,
    risk_level,
    next_action
):
    """
    Determine the best follow-up timing
    based on the sales conversation.
    """

    prompt = f"""
You are an expert sales follow-up strategist.

Analyze the following sales information and determine
the best time for the sales representative to follow up.

SALES CONVERSATION:
{conversation}

LEAD ANALYSIS:
{json.dumps(analysis, indent=2)}

LEAD SCORE:
{lead_score}/100

RISK LEVEL:
{risk_level}

NEXT BEST ACTION:
{json.dumps(next_action, indent=2)}

Choose an appropriate follow-up schedule.

Consider:
- Buying intent
- Urgency
- Explicit dates mentioned by the prospect
- Promises made by the prospect
- Requested information
- Buying stage
- Risk of losing the lead

Return ONLY valid JSON in this format:

{{
    "followup_days": 1,
    "timing": "Today",
    "reason": "The prospect requested pricing information immediately."
}}

Rules:
- followup_days must be an integer
- timing should be a short human-readable phrase
- reason should explain the decision
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a sales follow-up timing expert."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError:

        return {
            "followup_days": 1,
            "timing": "Tomorrow",
            "reason": "Default follow-up recommended."
        }