from datetime import datetime
import random
import string


def _rnd_id(length=8):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


class MyWorkspace:
    def __init__(
        self,
        id=None,
        name=None,
        path=None,
        tech_stack=None,
        start_command=None,
        test_command=None,
        allow_read=True,
        allow_write=False,
        allow_command=False,
        created_at=None,
        updated_at=None,
    ):
        now = datetime.now().isoformat()
        self.id = id or "W_" + _rnd_id()
        self.name = name or "Local Project"
        self.path = path or ""
        self.tech_stack = tech_stack or ""
        self.start_command = start_command or ""
        self.test_command = test_command or ""
        self.allow_read = allow_read if allow_read is not None else True
        self.allow_write = allow_write if allow_write is not None else False
        self.allow_command = allow_command if allow_command is not None else False
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def touch(self):
        self.updated_at = datetime.now().isoformat()
