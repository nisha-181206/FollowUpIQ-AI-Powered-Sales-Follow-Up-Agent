from datetime import datetime, timedelta


def calculate_snooze_date(days):
    """
    Calculate a future date for snoozing a lead.
    """

    return datetime.now() + timedelta(days=days)


def get_snooze_options():
    """
    Available snooze options for the salesperson.
    """

    return {
        "Tomorrow": 1,
        "In 3 Days": 3,
        "Next Week": 7
    }


def validate_followup_message(subject, message):
    """
    Basic validation before a follow-up is approved.
    """

    if not subject or not subject.strip():
        return False, "Subject cannot be empty."

    if not message or not message.strip():
        return False, "Follow-up message cannot be empty."

    if len(message.strip()) < 20:
        return False, "Follow-up message is too short."

    return True, "Message is ready."


def prepare_followup(subject, message):
    """
    Prepare a follow-up for human approval.
    """

    valid, reason = validate_followup_message(
        subject,
        message
    )

    return {
        "approved": False,
        "valid": valid,
        "status": "Ready for Review" if valid else "Needs Editing",
        "reason": reason,
        "subject": subject.strip(),
        "message": message.strip()
    }