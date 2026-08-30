import streamlit as st
from database.lead_db import update_lead_status
from database.lead_db import clear_all_leads
from workflow.sales_graph import create_sales_graph
from lead_actions import (
    get_snooze_options,
    calculate_snooze_date,
    prepare_followup
)
from database.lead_db import (
    create_database,
    get_all_leads,
    update_lead_status,
    get_lead_statistics,
    get_followup_status,
    get_followup_statistics,
    get_smart_followup_list,
    snooze_lead
)

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="FollowUpIQ",
    page_icon="🚀",
    layout="wide"
)


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

create_database()


# ==========================================================
# HEADER
# ==========================================================

st.title("🚀 FollowUpIQ")

st.subheader("AI-Powered Sales Follow-Up Agent")

st.write(
    "Turn sales conversations into prioritized, "
    "actionable follow-ups."
)

st.divider()


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("⚡ FollowUpIQ")

    st.write(
        "Analyze prospects, detect follow-up risks, "
        "recommend the next best action, and generate "
        "personalized follow-ups."
    )

# ==========================================================
# DASHBOARD STATISTICS
# ==========================================================

stats = get_lead_statistics()

followup_stats = get_followup_statistics()

st.header("📊 Sales Follow-Up Overview")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        "Total Leads",
        stats["total"]
    )

with col2:
    st.metric(
        "🔥 Hot Leads",
        stats["hot"]
    )

with col3:
    st.metric(
        "⚠️ High Risk",
        stats["at_risk"]
    )

with col4:
    st.metric(
        "🔴 Overdue",
        followup_stats["overdue"]
    )

with col5:
    st.metric(
        "🟠 Due Today",
        followup_stats["today"]
    )

with col6:
    st.metric(
        "🟢 Upcoming",
        followup_stats["upcoming"]
    )

    st.divider()

    st.info(
        "AI Pipeline:\n\n"
        "Conversation → Analysis → Score → Risk → "
        "Next Action → Follow-Up"
    )


# ==========================================================
# INPUT SECTION
# ==========================================================

st.header("📝 Analyze a Sales Conversation")

conversation = st.text_area(
    "Paste the sales conversation, email, or meeting notes:",
    height=220,
    placeholder=(
        "Example:\n\n"
        "Hi Rahul,\n\n"
        "Thanks for attending our product demo. "
        "I really liked the enterprise plan and the "
        "reporting features. Please send me the pricing "
        "details. I'll discuss it with my manager tomorrow."
    )
)


analyze_button = st.button(
    "🚀 Analyze Lead",
    type="primary",
    use_container_width=True
)


# ==========================================================
# RUN AI AGENT
# ==========================================================

if analyze_button:

    if not conversation.strip():

        st.warning(
            "Please enter a sales conversation first."
        )

    else:

        with st.spinner(
            "🤖 FollowUpIQ is analyzing the prospect..."
        ):

            try:

                sales_agent = create_sales_graph()

                result = sales_agent.invoke({
                    "conversation": conversation
                })

                st.session_state["result"] = result

            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )


# ==========================================================
# DISPLAY RESULT
# ==========================================================

if "result" in st.session_state:

    result = st.session_state["result"]

    analysis = result["analysis"]
    action = result["next_action"]
    followup = result["followup"]
    timing = result["followup_timing"]

    st.subheader("⏰ AI Recommended Follow-Up")

    st.info(
        f"**{timing.get('timing', 'Tomorrow')}**"
    )

    st.write(
        f"**Why:** {timing.get('reason', '')}"
    )


    st.divider()

    st.header("📊 Lead Intelligence")


    # ------------------------------------------------------
    # METRICS
    # ------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Lead Score",
            f"{result['lead_score']}/100"
        )


    with col2:

        st.metric(
            "Priority",
            result["lead_priority"]
        )


    with col3:

        st.metric(
            "Risk Score",
            f"{result['risk_score']}/100"
        )


    with col4:

        st.metric(
            "Risk Level",
            result["risk_level"]
        )


    # ------------------------------------------------------
    # LEAD INFORMATION
    # ------------------------------------------------------

    st.subheader("👤 Prospect Information")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Name:** "
            f"{analysis.get('lead_name', 'Unknown')}"
        )

        st.write(
            f"**Company:** "
            f"{analysis.get('company', 'Unknown')}"
        )

    with col2:

        st.write(
            f"**Buying Intent:** "
            f"{analysis.get('buying_intent', 'Unknown')}"
        )

        st.write(
            f"**Buying Stage:** "
            f"{analysis.get('buying_stage', 'Unknown')}"
        )


    # ------------------------------------------------------
    # BUYING SIGNALS
    # ------------------------------------------------------

    st.subheader("🔥 Buying Signals")

    signals = analysis.get(
        "buying_signals",
        []
    )

    if signals:

        for signal in signals:

            st.success(
                f"✓ {signal}"
            )

    else:

        st.write("No strong buying signals detected.")


    # ------------------------------------------------------
    # OBJECTIONS
    # ------------------------------------------------------

    st.subheader("⚠️ Objections")

    objections = analysis.get(
        "objections",
        []
    )

    if objections:

        for objection in objections:

            st.warning(
                f"• {objection}"
            )

    else:

        st.write(
            "No major objections detected."
        )


    # ------------------------------------------------------
    # NEXT BEST ACTION
    # ------------------------------------------------------

    st.divider()

    st.header("🎯 Next Best Action")

    st.info(
        f"**{action.get('next_action', 'Unknown')}**"
    )

    st.write(
        f"**Urgency:** "
        f"{action.get('urgency', 'Unknown')}"
    )

    st.write(
        f"**Why:** "
        f"{action.get('reason', 'Unknown')}"
    )

    st.write(
        f"**Suggested Timing:** "
        f"{action.get('suggested_timing', 'Unknown')}"
    )


    # ------------------------------------------------------
    # FOLLOW-UP MESSAGE
    # ------------------------------------------------------

    st.divider()
    st.subheader("✉️ AI-Generated Follow-Up")

    subject = st.text_input(
        "Subject",
        value=followup.get("subject", "")
    )

    message = st.text_area(
        "Message",
        value=followup.get("message", ""),
        height=180
    )

    if "followup_reviewed" not in st.session_state:
        st.session_state["followup_reviewed"] = False

    if "followup_approved" not in st.session_state:
        st.session_state["followup_approved"] = False


    if st.button("🔍 Review Follow-Up"):

        review = prepare_followup(
            subject,
            message
        )

        if review["valid"]:

            st.session_state["followup_reviewed"] = True

            st.success(
                "✅ Follow-up is ready for approval."
            )

            st.write(
                f"**Status:** {review['status']}"
            )

        else:

            st.session_state["followup_reviewed"] = False

            st.warning(
                f"⚠️ {review['reason']}"
            )


    if st.session_state["followup_reviewed"]:

            st.divider()

            st.subheader("👤 Human Approval")

            st.info(
                    "Review the AI-generated follow-up before approving it."
            )

            # 1️⃣ APPROVE
            
            if st.button(
                    "✅ Approve Follow-Up",
                    use_container_width=True,
                    key="approve_followup_button"
            ):

                    st.session_state["followup_approved"] = True

                    lead_id = result.get("lead_id")

                    if lead_id:
                            update_lead_status(
                                lead_id,
                                "Approved"
                            )

                            st.success(
                                "✅ Follow-up approved by salesperson."
                            )

            # 2️⃣ NEEDS EDITING
            if st.button(
                    "✏️ Needs Editing",
                    use_container_width=True,
                    key="edit_followup_button"
                ):

                    st.session_state["followup_approved"] = False
                    st.session_state["followup_reviewed"] = False

                    st.warning(
                            "✏️ Follow-up sent back for editing."
                    )

            # 3️⃣ SNOOZE
            st.divider()
            
            st.subheader("⏰ Snooze Follow-Up")

            snooze_options = {
                    "Tomorrow": 1,
                    "In 3 Days": 3,
                    "Next Week": 7
            }

            selected_snooze = st.selectbox(
                    "Remind me:",
                    list(snooze_options.keys())
            )

            if st.button(
                    "⏰ Snooze Lead",
                    use_container_width=True,
                    key="snooze_lead_button"
            ):

                    lead_id = result.get("lead_id")

                    if lead_id:

                        snooze_lead(
                            lead_id,
                            snooze_options[selected_snooze]
                        )

                        st.success(
                            f"⏰ Lead snoozed until {selected_snooze}."
                        )

            # 4️⃣ COMPLETED
            st.divider()

            st.subheader("✔️ Lead Status")

            if st.button(
                "✔️ Mark Lead as Completed",
                use_container_width=True,
                key="complete_lead_button"
            ):

                lead_id = result.get("lead_id")

                if lead_id:

                    update_lead_status(
                        lead_id,
                        "Completed"
                )

                    st.success(
                        "✅ Lead marked as completed."
                    )

    col1, col2 = st.columns(2)

    with col1:

                st.session_state["followup_approved"] = True

                lead_id = result.get("lead_id")

                if lead_id:

                    update_lead_status(
                        lead_id,
                        "Approved"
                    )

                    st.success(
                        "✅ Follow-up approved by salesperson."
                    )

                else:

                    st.warning(
                        "⚠️ Lead ID not found. Approval was not saved."
                    )

    with col2:

                st.session_state["followup_approved"] = False

                st.session_state["followup_reviewed"] = False

                st.warning(
                    "✏️ Follow-up sent back for editing."
                )
    
    # ------------------------------------------------------
    # PERSONALIZATION
    # ------------------------------------------------------

    st.subheader(
        "🎯 Personalization Used"
    )

    points = followup.get(
        "personalization_points",
        []
    )

    for point in points:

        st.write(
            f"✓ {point}"
        )


# ==========================================================
# PRIORITIZED FOLLOW-UP LIST
# ==========================================================

st.divider()
with st.expander("🧹 Database Cleanup"):

    st.warning(
        "This will remove ALL existing leads and give you "
        "a completely fresh dashboard."
    )

    if st.button(
        "🗑️ Clear All Leads",
        type="secondary"
    ):

        deleted = clear_all_leads()

        st.success(
            f"✅ Cleared {deleted} leads."
        )

        st.rerun()

st.header("📋 Prioritized Follow-Up List")

leads = get_smart_followup_list()


if not leads:

    st.info(
        "No leads have been analyzed yet."
    )

else:

    for lead in leads:
        followup_status = get_followup_status(
            lead["followup_due"],
            lead["status"]
        )

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.write(
                    f"**{lead['lead_name']}**"
                )

                st.caption(
                    lead["company"]
                )

                st.write(
                    f"Status: **{lead['status']}**"
                )

            with col2:

                st.write(
                    f"🔥 Score: "
                    f"{lead['lead_score']}/100"
                )

                st.write(
                    f"Priority: "
                    f"{lead['lead_priority']}"
                )

            with col3:

                st.write(
                    f"⚠️ Risk: "
                    f"{lead['risk_level']}"
                )

                st.write(
                    f"Risk Score: "
                    f"{lead['risk_score']}/100"
                )

            with col4:

                st.write(
                    f"🎯 {lead['next_action']}"
                )

                st.write(
                    f"Urgency: "
                    f"{lead['urgency']}"
                )

                st.write(
                    f"📅 Due: "
                    f"{lead['followup_due']}"
                )

            col5, col6 = st.columns(2)

            with col5:

                if lead["status"] == "Pending":

                    if st.button(
                        "✅ Mark Completed",
                        key=f"complete_{lead['id']}"
                    ):

                        update_lead_status(
                            lead["id"],
                            "Completed"
                        )

                        st.rerun()

            with col6:

                if lead["status"] == "Pending":

                    if st.button(
                        "⏰ Snooze",
                        key=f"snooze_{lead['id']}"
                    ):

                        update_lead_status(
                            lead["id"],
                            "Snoozed"
                        )

                        st.rerun()
