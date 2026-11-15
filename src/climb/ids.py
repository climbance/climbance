import hashlib
import json
import uuid


# Opaque and unguessable: nothing derives an id from a record's content, or two
# engines would mint the same id for different records.
def new_id() -> str:
    return uuid.uuid4().hex


def settings_hash(settings: object) -> str:
    """Names a set of settings by content, so a stored reading says which model
    made it."""
    encoded = json.dumps(settings, sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()[:12]


__all__ = ["new_id", "settings_hash"]
