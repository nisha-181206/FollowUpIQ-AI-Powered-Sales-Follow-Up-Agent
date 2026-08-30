from groq import Groq
from config import GROQ_API_KEY
import json
import re


# ==========================================================
# CREATE GROQ CLIENT
# ==========================================================

client = Groq(api_key=GROQ_API_KEY)


# ==========================================================
# SALES CONVERSATION ANALYZER
# ==========================================================

def analyze_conversation(conversation: str):

    prompt = f"""
You are FollowUpIQ, an AI Sales Conversation Intelligence Agent.

Analyze the following sales conversation.

SALES CONVERSATION:
{conversation}

IMPORTANT:

The prospect/customer is the person who is interested in
the product, asks questions, requests pricing, discusses
purchase, or talks about their manager/company.

If the conversation starts with:

"Hi Rahul"

then Rahul is the prospect unless the conversation
clearly says otherwise.

Do NOT confuse the sales representative with the prospect.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "lead_name": "Unknown",
    "company": "Unknown",
    "buying_intent": "High",
    "buying_stage": "Consideration",
    "timeline": "Unknown",
    "pain_points": [],
    "decision_maker": "Unknown",
    "buying_signals": [],
    "objections": []
}}

RULES:

1. lead_name:
Extract the prospect's name if clearly available.

Example:
"Hi Rahul" → "Rahul"

2. company:
Extract the prospect's company only if explicitly mentioned.
Otherwise use "Unknown".

3. buying_intent:
Must be exactly:
"High", "Medium", or "Low".

4. buying_stage:
Must be exactly:
"Awareness", "Consideration", "Decision", or "Not Ready".

5. timeline:
Extract timing such as:
"Today"
"Tomorrow"
"Next week"
"Within a month"

6. pain_points:
Only include actual problems mentioned.

7. decision_maker:
Extract manager, CTO, finance team, etc. if mentioned.

8. buying_signals:
Include specific positive signals such as:
"Interested in enterprise plan"
"Requested pricing"
"Asked about implementation"

9. objections:
Only include actual objections or concerns.

10. NEVER invent information.

11. If information is unavailable, use:
"Unknown"

12. Return ONLY JSON.
"""


    # ======================================================
    # CALL GROQ
    # ======================================================

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise sales intelligence agent. "
                    "Identify the prospect correctly. "
                    "Never invent names or companies."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0,

        response_format={
            "type": "json_object"
        }
    )


    # ======================================================
    # PARSE RESPONSE
    # ======================================================

    result_text = response.choices[0].message.content

    result = json.loads(result_text)


    # ======================================================
    # NAME FALLBACK
    # ======================================================

    name = result.get("lead_name", "Unknown")


    if not name or name.lower() == "unknown":

        patterns = [

            r"\bHi\s+([A-Z][a-z]+)\b",

            r"\bHello\s+([A-Z][a-z]+)\b",

            r"\bHey\s+([A-Z][a-z]+)\b",

            r"\bDear\s+([A-Z][a-z]+)\b"

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                conversation
            )

            if match:

                result["lead_name"] = match.group(1)

                break


    # ======================================================
    # FINAL SAFETY
    # ======================================================

    if not result.get("lead_name"):

        result["lead_name"] = "Unknown"


    if not result.get("company"):

        result["company"] = "Unknown"


    return result


# ==========================================================
# DEMO / TEST
# ==========================================================

if __name__ == "__main__":

    conversation = """
    Hi Rahul,

    I am interested in your enterprise plan.
    Please send me pricing.

    I will discuss it with my manager tomorrow.
    """


    print("=" * 60)

    print("FOLLOWUPIQ - SALES CONVERSATION ANALYZER")

    print("=" * 60)


    result = analyze_conversation(
        conversation
    )


    print("\nAI ANALYSIS")

    print("-" * 60)


    for key, value in result.items():

        print(
            f"{key}: {value}"
        )
