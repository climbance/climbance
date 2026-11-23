from climb.measured import chance_loss
from climb.storage import Database


def chance_loss_printed(root: Database) -> None:
    found = chance_loss(root)
    held = "none" if found.log_loss is None else f"{found.log_loss:.4f}"
    print(f"log-loss {held} over {found.sittings} cold sittings of {found.users} users")
    print(f"gap {found.gap:.0f} points")
