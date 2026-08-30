from groq import Groq
from config import GROQ_API_KEY
import json


client = Groq(api_key=GROQ_API_KEY)


def recommend_next_action(
    analysis,
    lead_score,
    risk_score,
    days_since_contact
):
    """
    Recommend the best next action for a sales representative.
    """

    prompt = f"""
You are FollowUpIQ, an AI Sales Decision Agent.

Your job is to determine the BEST NEXT ACTION
for a sales representative based on the available
lead intelligence.

LEAD ANALYSIS:
{json.dumps(analysis, indent=2)}

LEAD SCORE:
{lead_score}/100

RISK SCORE:
{risk_score}/100

DAYS SINCE LAST CONTACT:
{days_since_contact}

Choose ONE primary action from:

- Send Follow-Up Email
- Call Prospect
- Schedule Demo
- Send Pricing
- Address Objection
- Schedule Decision-Maker Meeting
- Re-Engage Lead
- Wait for Response
- Escalate to Sales Manager

Return ONLY valid JSON:

{{
    "next_action": "",
    "urgency": "",
    "reason": "",
    "suggested_timing": ""
}}

Rules:

1. urgency must be:
   "Immediate", "Today", "This Week", or "Low"

2. Choose the action based on evidence from the
   conversation.

3. Do not invent information.

4. High-risk leads should receive more urgent actions.

5. If pricing was requested, consider "Send Pricing".

6. If a demo was requested, consider "Schedule Demo".

7. If there are objections, consider "Address Objection".

8. If there has been no response for several days,
   consider "Re-Engage Lead" or "Call Prospect".

9. Keep the reason short but specific.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a precise sales decision-making agent."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content

    return json.loads(result)


# ======================================================
# DEMO / TEST
# ======================================================

if __name__ == "__main__":

    sample_analysis = {
        "lead_name": "Rahul",
        "company": "ABC Technologies",
        "buying_intent": "High",
        "buying_stage": "Decision",
        "timeline": "Tomorrow",
        "pain_points": [],
        "decision_maker": "Manager",
        "buying_signals": [
            "Requested enterprise pricing",
            "Interested in enterprise plan",
            "Manager discussion planned"
        ],
        "objections": []
    }

    lead_score = 91
    risk_score = 80
    days_since_contact = 5

    result = recommend_next_action(
        sample_analysis,
        lead_score,
        risk_score,
        days_since_contact
    )

    print("\n" + "=" * 60)
    print("FOLLOWUPIQ - NEXT BEST ACTION")
    print("=" * 60)

    print(f"\n🎯 Next Action     : {result['next_action']}")
    print(f"🚨 Urgency         : {result['urgency']}")
    print(f"💡 Reason          : {result['reason']}")
    print(f"⏰ Suggested Timing: {result['suggested_timing']}")

    print("\n" + "=" * 60)