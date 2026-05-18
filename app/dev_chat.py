from llms import create_llm
from workspace_fs import WorkspacePathError, build_file_tree, format_file_tree


class DevChatError(RuntimeError):
    pass


def _permission_summary(workspace):
    permissions = [
        "允许读取文件" if workspace.allow_read else "不允许读取文件",
        "允许写入文件" if workspace.allow_write else "不允许写入文件",
        "允许运行命令" if workspace.allow_command else "不允许运行命令",
    ]
    return "，".join(permissions)


def _workspace_file_tree_text(workspace):
    if not workspace.allow_read:
        return "当前工作区未开启文件读取权限，不能读取文件树。"
    try:
        return format_file_tree(build_file_tree(workspace.path))
    except WorkspacePathError as exc:
        raise DevChatError(str(exc)) from exc


def _action_protocol(workspace):
    write_protocol = (
        '如需写入文件，请输出代码块：```file path="relative/path"\\n完整文件内容\\n```。'
        if workspace.allow_write
        else "写入权限未开启，不要输出文件写入代码块。"
    )
    command_protocol = (
        f'如需运行测试命令，只能输出代码块：```command\\n{workspace.test_command}\\n```。'
        if workspace.allow_command and workspace.test_command
        else "命令权限未开启或未配置测试命令，不要请求运行命令。"
    )
    return "\n".join([write_protocol, command_protocol])


def _conversation_text(session):
    role_labels = {
        "user": "用户",
        "assistant": "助手",
    }
    lines = []
    for message in session.messages:
        role = role_labels.get(message["role"], message["role"])
        lines.append(f"{role}: {message['content']}")
    return "\n\n".join(lines)


def build_development_chat_prompt(session, workspace, file_tree_text):
    artifacts = []
    if session.plan.strip():
        artifacts.append(f"已有计划:\n{session.plan.strip()}")
    if session.diff.strip():
        artifacts.append(f"已有 Diff 预览:\n{session.diff.strip()}")
    if session.test_result.strip():
        artifacts.append(f"已有测试结果:\n{session.test_result.strip()}")
    if session.summary.strip():
        artifacts.append(f"已有总结:\n{session.summary.strip()}")

    artifacts_text = "\n\n".join(artifacts) or "暂无。"

    return f"""你是一个类似 Codex App 的本地项目开发助手。
你正在一个持续开发会话中回复用户。请基于工作区信息、文件树、已有产物和完整对话历史，给出下一条助手消息。

约束:
- 用中文回复。
- 可以分析、规划、指出需要查看的文件、建议下一步开发动作。
- 不要声称已经修改文件、运行命令或完成测试，除非上下文中已经明确有对应结果。
- 回复要像持续对话中的一条消息，避免重新输出整份 PRD。

可执行动作协议:
{_action_protocol(workspace)}

工作区:
- 项目名称: {workspace.name}
- 项目路径: {workspace.path}
- 技术栈说明: {workspace.tech_stack or "未填写"}
- 启动命令: {workspace.start_command or "未填写"}
- 测试命令: {workspace.test_command or "未填写"}
- 权限: {_permission_summary(workspace)}

文件树:
{file_tree_text}

已有产物:
{artifacts_text}

对话历史:
{_conversation_text(session)}
"""


def generate_development_reply(session, workspace, llm_factory=create_llm):
    if not session.llm_provider_model:
        raise DevChatError("开发会话没有选择执行模型。")
    if not session.messages:
        raise DevChatError("开发会话还没有消息。")

    file_tree_text = _workspace_file_tree_text(workspace)
    prompt = build_development_chat_prompt(session, workspace, file_tree_text)

    try:
        llm = llm_factory(session.llm_provider_model, temperature=0.2)
        response = llm.call(prompt)
    except Exception as exc:
        raise DevChatError(str(exc)) from exc

    reply = str(response or "").strip()
    if not reply:
        raise DevChatError("模型没有返回回复。")
    return reply
