from agents.timing import determine_followup_timing
from database.lead_db import create_database, save_lead
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from agents.analyzer import analyze_conversation
from agents.next_action import recommend_next_action
from agents.followup import generate_followup

from utils.scoring import calculate_lead_score
from utils.risk import calculate_risk


# ==========================================================
# 1. DEFINE AGENT STATE
# ==========================================================

class SalesState(TypedDict, total=False):

    conversation: str

    analysis: dict

    lead_score: int
    lead_priority: str

    risk_score: int
    risk_level: str

    next_action: dict

    followup_timing: dict

    followup: dict

    lead_id: int


# ==========================================================
# 2. ANALYZE CONVERSATION
# ==========================================================

def analyze_node(state: SalesState):

    print("\n🤖 Analyzing sales conversation...")

    analysis = analyze_conversation(
        state["conversation"]
    )

    return {
        "analysis": analysis
    }


# ==========================================================
# 3. CALCULATE LEAD SCORE
# ==========================================================

def scoring_node(state: SalesState):

    print("📊 Calculating lead score...")

    result = calculate_lead_score(
        state["analysis"]
    )

    return {
        "lead_score": result["score"],
        "lead_priority": result["priority"]
    }


# ==========================================================
# 4. DETECT LEAD RISK
# ==========================================================

def risk_node(state: SalesState):

    print("⚠️ Detecting lead risk...")

    # For now we use a demo value.
    # Later this will come from the database.
    days_since_contact = 5

    result = calculate_risk(
        state["analysis"],
        state["lead_score"],
        days_since_contact
    )

    return {
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"]
    }


# ==========================================================
# 5. RECOMMEND NEXT BEST ACTION
# ==========================================================

def action_node(state: SalesState):

    print("🎯 Determining next best action...")

    result = recommend_next_action(
        state["analysis"],
        state["lead_score"],
        state["risk_score"],
        5
    )

    return {
        "next_action": result
    }


def timing_node(state: SalesState):

    print("⏰ Determining optimal follow-up timing...")

    timing = determine_followup_timing(
        conversation=state["conversation"],
        analysis=state["analysis"],
        lead_score=state["lead_score"],
        risk_level=state["risk_level"],
        next_action=state["next_action"]
    )

    return {
        "followup_timing": timing
    }


# ==========================================================
# 6. GENERATE PERSONALIZED FOLLOW-UP
# ==========================================================

def followup_node(state: SalesState):

    print("✉️ Generating personalized follow-up...")

    result = generate_followup(
        state["conversation"],
        state["analysis"],
        state["lead_score"],
        state["risk_score"],
        state["next_action"]
    )

    return {
        "followup": result
    }

# ==========================================================
# 7. SAVE LEAD TO DATABASE
# ==========================================================

def save_lead_node(state: SalesState):

    print("🗄️ Saving lead to database...")

    analysis = state["analysis"]
    action = state["next_action"]
    followup = state["followup"]

    # Get AI-recommended follow-up timing
    timing = state["followup_timing"]

    days_until_followup = timing.get(
        "followup_days",
        1
    )

    # Save lead
    lead_id = save_lead(
        lead_name=analysis.get("lead_name", "Unknown"),
        company=analysis.get("company", "Unknown"),
        conversation=state["conversation"],

        lead_score=state["lead_score"],
        lead_priority=state["lead_priority"],

        risk_score=state["risk_score"],
        risk_level=state["risk_level"],

        next_action=action.get(
            "next_action",
            "Unknown"
        ),

        urgency=action.get(
            "urgency",
            "Unknown"
        ),

        followup_subject=followup.get(
            "subject",
            ""
        ),

        followup_message=followup.get(
            "message",
            ""
        ),

        days_until_followup=days_until_followup
    )

    return {
        "lead_id": lead_id
    }

# ==========================================================
# 7. BUILD LANGGRAPH
# ==========================================================

def create_sales_graph():

    graph = StateGraph(SalesState)

    graph.add_node("analyze", analyze_node)
    graph.add_node("score", scoring_node)
    graph.add_node("risk", risk_node)
    graph.add_node("next_action", action_node)
    graph.add_node("followup", followup_node)
    graph.add_node("save_lead", save_lead_node)
    graph.add_node("timing", timing_node)

    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "score")
    graph.add_edge("score", "risk")
    graph.add_edge("risk", "next_action")
    graph.add_edge("next_action", "timing")
    graph.add_edge("timing", "followup")
    # Follow-up → Database
    graph.add_edge("followup", "save_lead")

    # Database → End
    graph.add_edge("save_lead", END)

    return graph.compile()

# ==========================================================
# 8. RUN DEMO
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

    print("\n")
    print("=" * 70)
    print("🚀 FOLLOWUPIQ - AI SALES FOLLOW-UP AGENT")
    print("=" * 70)

    create_database()
    sales_agent = create_sales_graph()

    result = sales_agent.invoke({
        "conversation": conversation
    })

    print("\n")
    print("=" * 70)
    print("📋 FINAL SALES INTELLIGENCE")
    print("=" * 70)

    print("\n👤 Lead:")
    print(result["analysis"].get("lead_name"))

    print("\n🏢 Company:")
    print(result["analysis"].get("company"))

    print("\n🔥 Lead Score:")
    print(
        f"{result['lead_score']}/100 "
        f"({result['lead_priority']})"
    )

    print("\n⚠️ Risk:")
    print(
        f"{result['risk_score']}/100 "
        f"({result['risk_level']})"
    )

    print("\n🎯 Next Best Action:")
    print(
        result["next_action"].get("next_action")
    )

    print("\n🚨 Urgency:")
    print(
        result["next_action"].get("urgency")
    )

    print("\n💡 Reason:")
    print(
        result["next_action"].get("reason")
    )

    print("\n✉️ FOLLOW-UP MESSAGE")
    print("-" * 70)

    print(
        result["followup"].get("subject")
    )

    print()

    print(
        result["followup"].get("message")
    )

    print("\n🗄️ Lead ID:")
    print(result["lead_id"])

    print("\n")
    print("=" * 70)
    print("✅ FOLLOWUPIQ ANALYSIS COMPLETE")
    print("=" * 70)