from groq import Groq
from config import GROQ_API_KEY
import json


# Create Groq client
client = Groq(api_key=GROQ_API_KEY)


def analyze_conversation(conversation: str):
    """
    Analyze a sales conversation and extract
    important lead information.
    """

    prompt = f"""
You are FollowUpIQ, an AI Sales Conversation Intelligence Agent.

Your job is to analyze a sales conversation and extract
useful information about the prospect.

SALES CONVERSATION:
{conversation}

Return ONLY valid JSON in exactly this structure:

{{
    "lead_name": "",
    "company": "",
    "buying_intent": "",
    "buying_stage": "",
    "timeline": "",
    "pain_points": [],
    "decision_maker": "",
    "buying_signals": [],
    "objections": []
}}

Rules:

1. buying_intent must be:
   "High", "Medium", or "Low"

2. buying_stage must be:
   "Awareness", "Consideration", "Decision", or "Not Ready"

3. If information is not available, write:
   "Unknown"

4. Do NOT invent information.

5. buying_signals must contain specific positive
   signals from the conversation.

6. objections must contain specific concerns
   mentioned by the prospect.

7. Keep the analysis concise and factual.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a precise sales intelligence agent."
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


# ==========================================================
# DEMO / TEST
# ==========================================================

if __name__ == "__main__":

    conversation = """
    Hi Rahul,

    Thanks for attending our product demo.

    I really liked the enterprise plan and the reporting features.
    Please send me the enterprise pricing details.

    I'll discuss the pricing with my manager tomorrow
    and get back to you.

    Thanks.
    """

    print("\n" + "=" * 60)
    print("FOLLOWUPIQ - SALES CONVERSATION ANALYZER")
    print("=" * 60)

    result = analyze_conversation(conversation)

    print("\nSALES CONVERSATION:")
    print(conversation)

    print("\n" + "-" * 60)
    print("AI ANALYSIS")
    print("-" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 60)
