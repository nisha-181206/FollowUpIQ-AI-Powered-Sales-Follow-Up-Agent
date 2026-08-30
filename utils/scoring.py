def calculate_lead_score(analysis):
    """
    Calculate a lead score from 0 to 100
    using the AI-generated conversation analysis.
    """

    score = 0
    reasons = []

    # --------------------------------------------------
    # 1. BUYING INTENT
    # --------------------------------------------------

    intent = analysis.get("buying_intent", "").lower()

    if intent == "high":
        score += 30
        reasons.append("High buying intent")

    elif intent == "medium":
        score += 20
        reasons.append("Medium buying intent")

    elif intent == "low":
        score += 5


    # --------------------------------------------------
    # 2. BUYING STAGE
    # --------------------------------------------------

    stage = analysis.get("buying_stage", "").lower()

    if stage == "decision":
        score += 20
        reasons.append("Prospect is in decision stage")

    elif stage == "consideration":
        score += 15
        reasons.append("Prospect is considering the solution")

    elif stage == "awareness":
        score += 5


    # --------------------------------------------------
    # 3. TIMELINE
    # --------------------------------------------------

    timeline = analysis.get("timeline", "").lower()

    urgent_words = [
        "today",
        "tomorrow",
        "this week",
        "within",
        "immediately",
        "soon"
    ]

    if any(word in timeline for word in urgent_words):
        score += 20
        reasons.append("Immediate buying timeline")

    elif timeline != "unknown" and timeline:
        score += 10
        reasons.append("Buying timeline identified")


    # --------------------------------------------------
    # 4. BUYING SIGNALS
    # --------------------------------------------------

    buying_signals = analysis.get("buying_signals", [])

    if buying_signals:
        signal_points = min(len(buying_signals) * 5, 15)

        score += signal_points

        reasons.append(
            f"{len(buying_signals)} buying signal(s) detected"
        )


    # --------------------------------------------------
    # 5. DECISION MAKER
    # --------------------------------------------------

    decision_maker = analysis.get("decision_maker", "").lower()

    if decision_maker and decision_maker != "unknown":
        score += 10
        reasons.append("Decision maker identified")


    # --------------------------------------------------
    # MAKE SURE SCORE IS BETWEEN 0 AND 100
    # --------------------------------------------------

    score = min(score, 100)


    # --------------------------------------------------
    # PRIORITY CLASSIFICATION
    # --------------------------------------------------

    if score >= 80:
        priority = "HOT"

    elif score >= 50:
        priority = "WARM"

    else:
        priority = "COLD"


    return {
        "score": score,
        "priority": priority,
        "reasons": reasons
    }


# ======================================================
# TEST THE SCORING SYSTEM
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

    result = calculate_lead_score(sample_analysis)

    print("\n" + "=" * 50)
    print("FOLLOWUPIQ - LEAD SCORING")
    print("=" * 50)

    print(f"\nLead Score : {result['score']}/100")
    print(f"Priority   : {result['priority']}")

    print("\nWhy this score?")

    for reason in result["reasons"]:
        print(f"✓ {reason}")

    print("\n" + "=" * 50)