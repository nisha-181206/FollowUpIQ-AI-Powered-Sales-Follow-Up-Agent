from groq import Groq
from config import GROQ_API_KEY
import json


client = Groq(api_key=GROQ_API_KEY)


def generate_followup(
    conversation,
    analysis,
    lead_score,
    risk_score,
    next_action
):
    """
    Generate a personalized sales follow-up message
    based on the prospect's actual conversation.
    """

    prompt = f"""
You are FollowUpIQ, an AI Sales Follow-Up Agent.

Create a personalized follow-up message for a sales
representative using the information below.

ORIGINAL SALES CONVERSATION:
{conversation}

LEAD ANALYSIS:
{json.dumps(analysis, indent=2)}

LEAD SCORE:
{lead_score}/100

RISK SCORE:
{risk_score}/100

RECOMMENDED NEXT ACTION:
{next_action}

Return ONLY valid JSON:

{{
    "subject": "",
    "message": "",
    "personalization_points": [],
    "call_to_action": ""
}}

RULES:

1. The message must sound natural and professional.

2. Personalize the message using facts from the
   original conversation.

3. Do NOT invent company details, requirements,
   prices, dates, or promises.

4. Do NOT repeat the entire conversation.

5. Keep the message concise.

6. The message should clearly support the
   recommended next action.

7. If the next action is sending pricing, mention
   the pricing information naturally.

8. If the next action is addressing an objection,
   directly acknowledge the concern.

9. If the next action is re-engaging a lead,
   politely restart the conversation without sounding
   like spam.

10. Include a clear but non-pushy call to action.

11. personalization_points should contain 2-4 specific
    facts used from the conversation.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert B2B sales communication "
                    "assistant focused on helpful, personalized "
                    "follow-ups."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content

    return json.loads(result)


# ==========================================================
# DEMO
# ==========================================================

if __name__ == "__main__":

    conversation = """
    Hi Rahul,

    Thanks for attending our product demo.

    I really liked the enterprise plan and the reporting
    features. Please send me the enterprise pricing details.

    I'll discuss the pricing with my manager tomorrow
    and get back to you.

    Thanks.
    """

    analysis = {
        "lead_name": "Rahul",
        "company": "Unknown",
        "buying_intent": "High",
        "buying_stage": "Decision",
        "timeline": "Tomorrow",
        "pain_points": [],
        "decision_maker": "Manager",
        "buying_signals": [
            "Interested in enterprise plan",
            "Requested pricing",
            "Manager discussion planned"
        ],
        "objections": []
    }

    lead_score = 91
    risk_score = 80

    next_action = {
        "next_action": "Send Pricing",
        "urgency": "Immediate",
        "reason": "Prospect requested enterprise pricing.",
        "suggested_timing": "Today"
    }

    result = generate_followup(
        conversation,
        analysis,
        lead_score,
        risk_score,
        next_action
    )

    print("\n" + "=" * 65)
    print("FOLLOWUPIQ - PERSONALIZED FOLLOW-UP")
    print("=" * 65)

    print(f"\n📧 Subject:")
    print(result["subject"])

    print(f"\n💬 Message:")
    print(result["message"])

    print("\n🎯 Personalization Points:")

    for point in result["personalization_points"]:
        print(f"✓ {point}")

    print(f"\n👉 Call To Action:")
    print(result["call_to_action"])

    print("\n" + "=" * 65)