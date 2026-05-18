from llms import create_llm
from workspace_fs import WorkspacePathError, build_file_tree, format_file_tree


class DevPlanError(RuntimeError):
    pass


def _permission_summary(workspace):
    permissions = []
    permissions.append("允许读取文件" if workspace.allow_read else "不允许读取文件")
    permissions.append("允许写入文件" if workspace.allow_write else "不允许写入文件")
    permissions.append("允许运行命令" if workspace.allow_command else "不允许运行命令")
    return "；".join(permissions)


def _workspace_file_tree_text(workspace):
    if not workspace.allow_read:
        return "文件读取权限未开启，不能读取文件树。"
    try:
        return format_file_tree(build_file_tree(workspace.path))
    except WorkspacePathError as exc:
        raise DevPlanError(str(exc)) from exc


def build_development_plan_prompt(session, workspace, file_tree_text):
    return f"""你是一个谨慎的本地项目开发规划助手。

请基于下面的工作区信息和用户需求，只生成开发计划，不要直接输出代码、不要输出 diff、不要假装已经修改文件。

输出要求：
1. 用中文输出。
2. 先给出目标理解。
3. 再列出建议修改的文件或模块。
4. 再列出分步骤开发计划。
5. 最后列出验证方式和风险点。

工作区：
- 项目名称：{workspace.name}
- 项目路径：{workspace.path}
- 技术栈说明：{workspace.tech_stack or "未填写"}
- 启动命令：{workspace.start_command or "未填写"}
- 测试命令：{workspace.test_command or "未填写"}
- 权限：{_permission_summary(workspace)}

文件树：
{file_tree_text}

用户需求：
{session.requirement}
"""


def build_development_diff_prompt(session, workspace, file_tree_text):
    return f"""你是一个谨慎的本地项目代码修改助手。

请基于下面的用户需求、开发计划和文件树，生成 unified diff 预览。
不要声称已经写入文件，不要运行命令，不要输出与 diff 无关的解释。
如果上下文不足以生成可靠 diff，请在 diff 预览中用注释标明需要补充的信息。

工作区：
- 项目名称：{workspace.name}
- 项目路径：{workspace.path}
- 技术栈说明：{workspace.tech_stack or "未填写"}
- 权限：{_permission_summary(workspace)}

文件树：
{file_tree_text}

用户需求：
{session.requirement}

已有开发计划：
{session.plan}
"""


def generate_development_plan(session, workspace, llm_factory=create_llm):
    if not session.llm_provider_model:
        raise DevPlanError("开发会话没有选择执行模型。")

    file_tree_text = _workspace_file_tree_text(workspace)
    prompt = build_development_plan_prompt(session, workspace, file_tree_text)

    try:
        llm = llm_factory(session.llm_provider_model, temperature=0.1)
        response = llm.call(prompt)
    except Exception as exc:
        raise DevPlanError(str(exc)) from exc

    plan = str(response or "").strip()
    if not plan:
        raise DevPlanError("模型没有返回开发计划。")
    return plan


def generate_development_diff(session, workspace, llm_factory=create_llm):
    if not session.llm_provider_model:
        raise DevPlanError("开发会话没有选择执行模型。")
    if not session.plan.strip():
        raise DevPlanError("开发会话还没有开发计划。")

    file_tree_text = _workspace_file_tree_text(workspace)
    prompt = build_development_diff_prompt(session, workspace, file_tree_text)

    try:
        llm = llm_factory(session.llm_provider_model, temperature=0.1)
        response = llm.call(prompt)
    except Exception as exc:
        raise DevPlanError(str(exc)) from exc

    diff = str(response or "").strip()
    if not diff:
        raise DevPlanError("模型没有返回 Diff 预览。")
    return diff
