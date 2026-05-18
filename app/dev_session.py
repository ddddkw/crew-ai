from datetime import datetime
import random
import string


def _rnd_id(length=8):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


class DevSession:
    def __init__(
        self,
        id=None,
        workspace_id=None,
        requirement=None,
        llm_provider_model=None,
        messages=None,
        status=None,
        plan=None,
        logs=None,
        diff=None,
        test_result=None,
        summary=None,
        created_at=None,
        updated_at=None,
    ):
        now = datetime.now().isoformat()
        self.id = id or "D_" + _rnd_id()
        self.workspace_id = workspace_id
        self.requirement = requirement or ""
        self.llm_provider_model = llm_provider_model
        self.messages = self._normalize_messages(messages, self.requirement)
        self.status = status or "draft"
        self.plan = plan or ""
        self.logs = logs or []
        self.diff = diff or ""
        self.test_result = test_result or ""
        self.summary = summary or ""
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def touch(self):
        self.updated_at = datetime.now().isoformat()

    @staticmethod
    def _normalize_messages(messages, requirement):
        normalized = []
        for message in messages or []:
            if not isinstance(message, dict):
                continue
            role = str(message.get("role") or "").strip()
            content = str(message.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                normalized.append({"role": role, "content": content})

        if not normalized and requirement:
            normalized.append({"role": "user", "content": str(requirement).strip()})
        return normalized

    def add_message(self, role, content):
        role = str(role or "").strip()
        content = str(content or "").strip()
        if role not in {"user", "assistant"}:
            raise ValueError("Unsupported dev session message role.")
        if not content:
            return

        self.messages.append({"role": role, "content": content})
        if role == "user" and not self.requirement:
            self.requirement = content
