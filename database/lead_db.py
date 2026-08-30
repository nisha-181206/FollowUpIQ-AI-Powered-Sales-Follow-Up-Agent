import sqlite3
from datetime import datetime, timedelta


DATABASE_NAME = "database/followupiq.db"


def create_database():
    """Create the leads table if it does not exist."""

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            lead_name TEXT,
            company TEXT,

            conversation TEXT,

            lead_score INTEGER,
            lead_priority TEXT,

            risk_score INTEGER,
            risk_level TEXT,

            next_action TEXT,
            urgency TEXT,

            followup_subject TEXT,
            followup_message TEXT,

            last_contact TEXT,
            followup_due TEXT,

            status TEXT DEFAULT 'Pending',

            created_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_lead(
    lead_name,
    company,
    conversation,
    lead_score,
    lead_priority,
    risk_score,
    risk_level,
    next_action,
    urgency,
    followup_subject,
    followup_message,
    days_until_followup=1
):
    """Save a new lead to the database."""

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    now = datetime.now()

    followup_date = now + timedelta(
        days=days_until_followup
    )

    cursor.execute("""
        INSERT INTO leads (
            lead_name,
            company,
            conversation,
            lead_score,
            lead_priority,
            risk_score,
            risk_level,
            next_action,
            urgency,
            followup_subject,
            followup_message,
            last_contact,
            followup_due,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        lead_name,
        company,
        conversation,

        lead_score,
        lead_priority,

        risk_score,
        risk_level,

        next_action,
        urgency,

        followup_subject,
        followup_message,

        now.strftime("%Y-%m-%d %H:%M:%S"),

        followup_date.strftime("%Y-%m-%d %H:%M:%S"),

        "Pending",

        now.strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()

    lead_id = cursor.lastrowid

    connection.close()

    return lead_id


def get_all_leads():
    """Return all leads ordered by priority."""

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM leads
        ORDER BY
            CASE lead_priority
                WHEN 'HOT' THEN 1
                WHEN 'WARM' THEN 2
                WHEN 'COLD' THEN 3
            END,
            risk_score DESC,
            lead_score DESC
    """)

    leads = cursor.fetchall()

    connection.close()

    return leads

def get_followup_status(followup_due, status):
    """Determine the current follow-up status."""

    if status == "Completed":
        return "Completed"

    if status == "Snoozed":
        return "Snoozed"

    try:
        due_date = datetime.strptime(
            followup_due,
            "%Y-%m-%d %H:%M:%S"
        )

        now = datetime.now()

        if due_date < now:
            return "OVERDUE"

        elif due_date.date() == now.date():
            return "DUE TODAY"

        elif (due_date - now).days <= 2:
            return "DUE SOON"

        else:
            return "UPCOMING"

    except Exception:
        return "UNKNOWN"

def get_smart_followup_list():
    """Return leads ordered by follow-up urgency."""

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM leads
        WHERE status != 'Completed'
        ORDER BY
            CASE lead_priority
                WHEN 'HOT' THEN 1
                WHEN 'WARM' THEN 2
                WHEN 'COLD' THEN 3
                ELSE 4
            END,
            risk_score DESC,
            followup_due ASC
    """)

    leads = cursor.fetchall()

    connection.close()

    return leads

def get_followup_statistics():
    """Calculate follow-up urgency statistics."""

    leads = get_all_leads()

    overdue = 0
    today = 0
    soon = 0
    upcoming = 0

    for lead in leads:

        status = get_followup_status(
            lead["followup_due"],
            lead["status"]
        )

        if status == "OVERDUE":
            overdue += 1

        elif status == "DUE TODAY":
            today += 1

        elif status == "DUE SOON":
            soon += 1

        elif status == "UPCOMING":
            upcoming += 1

    return {
        "overdue": overdue,
        "today": today,
        "soon": soon,
        "upcoming": upcoming
    }

def update_lead_status(lead_id, status):
    """Update the status of a lead."""

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE leads
        SET status = ?
        WHERE id = ?
    """, (status, lead_id))

    connection.commit()
    connection.close()

def snooze_lead(lead_id, days):
    """Snooze a lead for a specified number of days."""

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    new_followup_date = datetime.now() + timedelta(days=days)

    cursor.execute("""
        UPDATE leads
        SET followup_due = ?,
            status = 'Snoozed'
        WHERE id = ?
    """, (
        new_followup_date.strftime("%Y-%m-%d %H:%M:%S"),
        lead_id
    ))

    connection.commit()
    connection.close()


def get_lead_statistics():
    """Return dashboard statistics."""

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM leads"
    )
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM leads
        WHERE lead_priority = 'HOT'
        AND status = 'Pending'
    """)
    hot = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM leads
        WHERE risk_level = 'HIGH'
        AND status = 'Pending'
    """)
    at_risk = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM leads
        WHERE status = 'Completed'
    """)
    completed = cursor.fetchone()[0]

    connection.close()

    return {
        "total": total,
        "hot": hot,
        "at_risk": at_risk,
        "completed": completed
    }

# ==========================================================
# TEST DATABASE
# ==========================================================

if __name__ == "__main__":

    create_database()

    lead_id = save_lead(
        lead_name="Rahul",
        company="ABC Technologies",
        conversation="Interested in enterprise plan.",
        lead_score=91,
        lead_priority="HOT",
        risk_score=80,
        risk_level="HIGH",
        next_action="Send Pricing",
        urgency="Immediate",
        followup_subject="Enterprise Plan Pricing",
        followup_message="Hi Rahul, sharing the pricing details...",
        days_until_followup=1
    )

    print("\n" + "=" * 55)
    print("FOLLOWUPIQ - DATABASE")
    print("=" * 55)

    print(f"\nLead saved successfully!")
    print(f"Lead ID: {lead_id}")

    print("\nPrioritized Leads:")

    leads = get_all_leads()

    for lead in leads:

        print(
            f"\n#{lead['id']} "
            f"{lead['lead_name']} | "
            f"{lead['lead_priority']} | "
            f"Score: {lead['lead_score']} | "
            f"Risk: {lead['risk_level']}"
        )
    

    print("\n" + "=" * 55)