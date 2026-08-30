def calculate_risk(analysis, lead_score, days_since_contact):
    """
    Calculate how likely a lead is to go cold.

    Parameters:
        analysis: AI analysis of the conversation
        lead_score: Current lead score (0-100)
        days_since_contact: Number of days since last contact
    """

    risk_score = 0
    reasons = []

    # --------------------------------------------------
    # 1. NO RESPONSE / TIME SINCE CONTACT
    # --------------------------------------------------

    if days_since_contact >= 7:
        risk_score += 40
        reasons.append("No contact for 7 or more days")

    elif days_since_contact >= 5:
        risk_score += 30
        reasons.append("No contact for 5 or more days")

    elif days_since_contact >= 3:
        risk_score += 20
        reasons.append("No contact for 3 or more days")

    elif days_since_contact >= 1:
        risk_score += 10
        reasons.append("No contact since previous interaction")


    # --------------------------------------------------
    # 2. HIGH BUYING INTENT + NO FOLLOW-UP
    # --------------------------------------------------

    intent = analysis.get("buying_intent", "").lower()

    if intent == "high" and days_since_contact >= 3:
        risk_score += 25
        reasons.append(
            "High buying intent but follow-up is delayed"
        )


    # --------------------------------------------------
    # 3. OBJECTIONS
    # --------------------------------------------------

    objections = analysis.get("objections", [])

    if objections:
        risk_score += 15
        reasons.append(
            f"{len(objections)} unresolved objection(s) detected"
        )


    # --------------------------------------------------
    # 4. DECISION STAGE
    # --------------------------------------------------

    stage = analysis.get("buying_stage", "").lower()

    if stage == "decision" and days_since_contact >= 3:
        risk_score += 15
        reasons.append(
            "Lead is in decision stage but follow-up is delayed"
        )


    # --------------------------------------------------
    # 5. HIGH-VALUE LEAD
    # --------------------------------------------------

    if lead_score >= 80 and days_since_contact >= 3:
        risk_score += 10
        reasons.append(
            "High-priority lead requires timely attention"
        )


    # --------------------------------------------------
    # LIMIT SCORE TO 100
    # --------------------------------------------------

    risk_score = min(risk_score, 100)


    # --------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------

    if risk_score >= 70:
        risk_level = "HIGH"

    elif risk_score >= 40:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"


    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons
    }


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    sample_analysis = {
        "buying_intent": "High",
        "buying_stage": "Decision",
        "objections": [
            "Needs manager approval"
        ]
    }

    lead_score = 91

    # Simulate no contact for 5 days
    days_since_contact = 5

    result = calculate_risk(
        sample_analysis,
        lead_score,
        days_since_contact
    )

    print("\n" + "=" * 55)
    print("FOLLOWUPIQ - LEAD RISK DETECTION")
    print("=" * 55)

    print(f"\nRisk Score : {result['risk_score']}/100")
    print(f"Risk Level : {result['risk_level']}")

    print("\nWhy is this lead at risk?")

    for reason in result["reasons"]:
        print(f"⚠ {reason}")

    print("\n" + "=" * 55)
