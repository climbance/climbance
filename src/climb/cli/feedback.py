from climb.log import FeedbackLog
from climb.storage import Database


def feedback_listed(root: Database) -> None:
    """Every user's feedback, newest first."""
    held = FeedbackLog(root).all()
    for one in reversed(held):
        when = one.created_at.date().isoformat()
        print(f"{when}  {one.user_id}  {one.client} {one.page}: {one.note}")
    print(f"{len(held)} notes of feedback")
