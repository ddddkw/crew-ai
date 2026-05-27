import re
import streamlit as st
from crewai import TaskOutput
from streamlit import session_state as ss
import threading
import ctypes
import queue
import time
import traceback
import os
import copy
from crew_run_loop import LoopConfig, run_crew_loop
from db_utils import load_results, save_result
from utils import format_result, generate_printable_view, rnd_id, get_tasks_outputs_str
from i18n import t


class PageCrewRun:
    def __init__(self):
        self.name = t("crew_run.title")
        self.maintain_session_state()
        if 'results' not in ss:
            ss.results = load_results()

    def get_tasks_output(self, tasks_output: list[TaskOutput], tasks=None):
        res = []

        index = 0
        for task_output in tasks_output:
            task_desc = None
            if tasks and index < len(tasks):
                task_desc = getattr(tasks[index], 'description', None)
            res.append({
                'raw': task_output.raw,
                'type': 'TaskOutput',
                'index': index,
                'description': task_desc
            })
            index += 1


        return res


    @staticmethod
    def maintain_session_state():
        defaults = {
            'crew_thread': None,
            'result': None,
            'running': False,
            'message_queue': queue.Queue(),
            'crew_runs': {},
            'crew_run_order': [],
            'selected_crew_name': None,
            'placeholders': {},
            'console_output': [],
            'last_update': time.time(),
            'console_expanded': True,
            'loop_enabled': False,
            'loop_count': 2,
            'loop_target_placeholder': None,
            'loop_run_id': None,
            'loop_rounds': [],
            'loop_stop_event': None,
        }
        for key, value in defaults.items():
            if key not in ss:
                ss[key] = value

    @staticmethod
    def extract_placeholders(text):
        return re.findall(r'\{(.*?)\}', text)

    def get_placeholders_from_crew(self, crew):
        placeholders = set()
        attributes = ['description', 'expected_output', 'role', 'backstory', 'goal']
        
        for task in crew.tasks:
            placeholders.update(self.extract_placeholders(task.description))
            placeholders.update(self.extract_placeholders(task.expected_output))
        
        for agent in crew.agents:
            for attr in attributes[2:]:
                placeholders.update(self.extract_placeholders(getattr(agent, attr)))
        
        return placeholders

    def run_crew(self, crewai_crew, inputs, message_queue):
        if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
            import agentops
            agentops.start_session()
        try:
            result = crewai_crew.kickoff(inputs=inputs)
            message_queue.put({"type": "run_complete", "result": result})
        except Exception as e:
            if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
                agentops.end_session()
            stack_trace = traceback.format_exc()
            print(f"Error running crew: {str(e)}\n{stack_trace}")
            message_queue.put({"type": "run_failed", "result": f"Error running crew: {str(e)}", "stack_trace": stack_trace})

    def run_crew_snapshot_thread(self, selected_crew, inputs, message_queue):
        try:
            crew = selected_crew.get_crewai_crew(full_output=True)
        except Exception as e:
            stack_trace = traceback.format_exc()
            print(f"Error preparing crew: {str(e)}\n{stack_trace}")
            message_queue.put({"type": "run_failed", "result": f"Error preparing crew: {str(e)}", "stack_trace": stack_trace})
            return

        self.run_crew(crew, inputs, message_queue)

    def run_crew_loop_thread(self, selected_crew, inputs, loop_config, message_queue, stop_event):
        if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
            import agentops
            agentops.start_session()
        try:
            run_crew_loop(
                crew_factory=lambda: selected_crew.get_crewai_crew(full_output=True),
                base_inputs=inputs,
                config=loop_config,
                message_queue=message_queue,
                stop_event=stop_event,
            )
        except Exception as e:
            if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
                agentops.end_session()
            stack_trace = traceback.format_exc()
            print(f"Error running crew loop: {str(e)}\n{stack_trace}")
            message_queue.put({"type": "loop_failed", "result": f"Error running crew loop: {str(e)}", "stack_trace": stack_trace})

    def get_mycrew_by_name(self, crewname):
        return next((crew for crew in ss.crews if crew.name == crewname), None)

    def has_running_runs(self):
        return any(run.get("status") == "running" for run in ss.get("crew_runs", {}).values())

    def sync_running_flag(self):
        running_runs = [run for run in ss.get("crew_runs", {}).values() if run.get("status") == "running"]
        ss.running = bool(running_runs)
        ss.crew_thread = running_runs[0].get("thread") if running_runs else None

    def run_status_label(self, status):
        labels = {
            "running": t("crew_run.run_status_running"),
            "completed": t("crew_run.run_status_completed"),
            "failed": t("crew_run.run_status_failed"),
            "stopped": t("crew_run.run_status_stopped"),
        }
        return labels.get(status, status)

    def append_run_log(self, run_state, message):
        run_state.setdefault("console_output", []).append(message)

    def finish_run(self, run_state, status):
        run_state["status"] = status
        run_state["thread"] = None
        run_state["finished_at"] = time.strftime("%H:%M:%S")
        self.sync_running_flag()

    def draw_cockpit_header(self, crew):
        running = self.has_running_runs()
        status_class = "is-running" if running else ""
        status_text = t("crew_run.status_running") if running else t("crew_run.status_idle")
        agent_count = len(crew.agents)
        task_count = len(crew.tasks)
        async_count = len([task for task in crew.tasks if task.async_execution])
        tool_count = len({tool.tool_id for agent in crew.agents for tool in agent.tools})
        manager = crew.manager_llm or (crew.manager_agent.role if crew.manager_agent else t("crew_run.no_manager"))

        st.markdown(
            f"""
            <div class="crew-run-cockpit">
              <div class="crew-run-title-row">
                <div>
                  <div class="crew-run-eyebrow">{t("crew_run.cockpit_eyebrow")}</div>
                  <div class="crew-run-title">{crew.name}</div>
                  <div class="crew-run-subtitle">{t("crew_run.cockpit_subtitle", manager=manager)}</div>
                </div>
                <div class="crew-run-status {status_class}">
                  <span class="crew-run-status-dot"></span>
                  <span>{status_text}</span>
                </div>
              </div>
              <div class="crew-run-metrics">
                <div class="crew-run-metric">
                  <div class="crew-run-metric-label">{t("crew_run.metric_agents")}</div>
                  <div class="crew-run-metric-value">{agent_count}</div>
                </div>
                <div class="crew-run-metric">
                  <div class="crew-run-metric-label">{t("crew_run.metric_tasks")}</div>
                  <div class="crew-run-metric-value">{task_count}</div>
                </div>
                <div class="crew-run-metric">
                  <div class="crew-run-metric-label">{t("crew_run.metric_async")}</div>
                  <div class="crew-run-metric-value">{async_count}</div>
                </div>
                <div class="crew-run-metric">
                  <div class="crew-run-metric-label">{t("crew_run.metric_tools")}</div>
                  <div class="crew-run-metric-value">{tool_count}</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def draw_panel_header(self, title, caption):
        st.markdown(
            f"""
            <div class="crew-run-panel">
              <div class="crew-run-panel-title">{title}</div>
              <div class="crew-run-panel-caption">{caption}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def draw_running_lock_notice(self):
        if not self.has_running_runs():
            return

        st.markdown(
            f'<div class="crew-run-lock-notice">{t("crew_run.running_lock_notice")}</div>',
            unsafe_allow_html=True,
        )

    def draw_placeholders(self, crew):
        placeholders = self.get_placeholders_from_crew(crew)
        if placeholders:
            st.markdown(f"#### {t('crew_run.placeholders')}")
            for placeholder in placeholders:
                placeholder_key = f'placeholder_{placeholder}'
                ss.placeholders[placeholder_key] = st.text_area(
                    label=placeholder,
                    key=placeholder_key,
                    value=ss.placeholders.get(placeholder_key, '')
                )

    def sync_loop_target_placeholder(self, placeholders):
        if ss.loop_target_placeholder not in placeholders:
            ss.loop_target_placeholder = None

        widget_key = "crew_run_loop_target_placeholder_control"
        if widget_key in ss and ss[widget_key] not in placeholders:
            del ss[widget_key]

    def draw_loop_controls(self, selected_crew):
        placeholders = sorted(self.get_placeholders_from_crew(selected_crew))
        self.sync_loop_target_placeholder(placeholders)
        st.markdown(f"#### {t('crew_run.loop_panel')}")
        st.caption(t("crew_run.loop_panel_caption"))

        ss.loop_enabled = st.checkbox(t("crew_run.loop_enabled"),
            value=bool(ss.loop_enabled),
            key="crew_run_loop_enabled_control",
        )

        if not ss.loop_enabled:
            return True

        if not placeholders:
            st.error(t("crew_run.loop_no_placeholders"))
            return False

        ss.loop_count = st.number_input(t("crew_run.loop_count"),
            min_value=2,
            max_value=20,
            value=max(2, int(ss.loop_count or 2)),
            step=1,
            key="crew_run_loop_count_control",
        )

        current_target = ss.loop_target_placeholder
        index = placeholders.index(current_target) if current_target in placeholders else 0
        ss.loop_target_placeholder = st.selectbox(t("crew_run.loop_target_placeholder"),
            options=placeholders,
            index=index,
            key="crew_run_loop_target_placeholder_control",
        )
        return bool(ss.loop_target_placeholder)

    def draw_loop_progress(self, loop_rounds=None):
        loop_rounds = ss.loop_rounds if loop_rounds is None else loop_rounds
        if not loop_rounds:
            return

        total = max([round_info.get("total", 1) for round_info in loop_rounds] or [1])
        completed = len([
            round_info for round_info in loop_rounds
            if round_info.get("status") in {"success", "failed", "stopped"}
        ])
        progress = min(1.0, completed / max(1, total))

        st.markdown(f"#### {t('crew_run.loop_progress')}")
        st.progress(progress)
        rows = []
        status_labels = {
            "waiting": t("crew_run.loop_status_waiting"),
            "running": t("crew_run.loop_status_running"),
            "success": t("crew_run.loop_status_success"),
            "failed": t("crew_run.loop_status_failed"),
            "stopped": t("crew_run.loop_status_stopped"),
        }
        for round_info in loop_rounds:
            status = round_info.get("status", "waiting")
            label = status_labels.get(status, status)
            rows.append(
                f'<div class="crew-run-loop-round is-{status}">'
                f'{t("crew_run.loop_round_status", index=round_info.get("index"), total=round_info.get("total"), status=label)}'
                f'</div>'
            )
        st.markdown(
            f'<div class="crew-run-loop-panel">{"".join(rows)}</div>',
            unsafe_allow_html=True,
        )

    def build_loop_config(self):
        return LoopConfig(
            enabled=bool(ss.loop_enabled),
            count=int(ss.loop_count or 1),
            target_placeholder=ss.loop_target_placeholder if ss.loop_enabled else None,
            loop_id=f"L_{rnd_id()}",
        )

    def current_inputs(self):
        return {key.split('_', 1)[1]: value for key, value in ss.placeholders.items() if key.startswith("placeholder_")}

    def update_run_loop_round(self, run_state, round_status):
        if not round_status:
            return
        rounds = [
            round_info for round_info in run_state.setdefault("loop_rounds", [])
            if round_info.get("index") != round_status.get("index")
        ]
        rounds.append(round_status)
        run_state["loop_rounds"] = sorted(rounds, key=lambda item: item.get("index", 0))

    def update_loop_round(self, round_status):
        if not round_status:
            return
        legacy_run = {"loop_rounds": ss.loop_rounds}
        self.update_run_loop_round(legacy_run, round_status)
        ss.loop_rounds = legacy_run["loop_rounds"]

    def apply_run_queue_message(self, run_state, message):
        message_type = message.get("type")
        if message_type in {"loop_round_start", "loop_round_success", "loop_failed", "loop_stopped", "loop_complete"}:
            self.update_run_loop_round(run_state, message.get("round"))

        if message_type == "loop_round_start":
            round_info = message.get("round") or {}
            self.append_run_log(
                run_state,
                t("crew_run.run_loop_round_started", index=round_info.get("index"), total=round_info.get("total")),
            )
            return

        if message_type == "loop_round_success":
            loop_metadata = dict(message.get("loop") or {})
            loop_metadata["round_input"] = dict((message.get("round") or {}).get("input") or {})
            run_state["result"] = {"result": message.get("result"), "loop": loop_metadata}
            round_info = message.get("round") or {}
            self.append_run_log(
                run_state,
                t("crew_run.run_loop_round_completed", index=round_info.get("index"), total=round_info.get("total")),
            )
            return

        if message_type == "loop_complete":
            loop_metadata = dict(message.get("loop") or {})
            loop_metadata["round_input"] = dict((message.get("round") or {}).get("input") or {})
            run_state["result"] = {"result": message.get("result"), "loop": loop_metadata}
            self.append_run_log(run_state, t("crew_run.run_completed_log"))
            self.finish_run(run_state, "completed")
            return

        if message_type == "loop_failed":
            run_state["result"] = message.get("result")
            if message.get("stack_trace"):
                self.append_run_log(run_state, message.get("stack_trace"))
            self.append_run_log(run_state, t("crew_run.run_failed_log"))
            self.finish_run(run_state, "failed")
            return

        if message_type == "loop_stopped":
            self.append_run_log(run_state, t("crew_run.run_stopped_log"))
            self.finish_run(run_state, "stopped")
            return

        if message_type == "run_complete":
            run_state["result"] = {"result": message.get("result")}
            self.append_run_log(run_state, t("crew_run.run_completed_log"))
            self.finish_run(run_state, "completed")
            return

        if message_type == "run_failed":
            run_state["result"] = message.get("result")
            if message.get("stack_trace"):
                self.append_run_log(run_state, message.get("stack_trace"))
            self.append_run_log(run_state, t("crew_run.run_failed_log"))
            self.finish_run(run_state, "failed")
            return

        if "result" in message:
            run_state["result"] = message
            self.append_run_log(run_state, t("crew_run.run_completed_log"))
            self.finish_run(run_state, "completed")

    def apply_loop_queue_message(self, message):
        legacy_run = {
            "id": "legacy",
            "status": "running",
            "result": ss.result,
            "loop_rounds": ss.loop_rounds,
            "console_output": ss.console_output if "console_output" in ss else [],
        }
        self.apply_run_queue_message(legacy_run, message)
        ss.loop_rounds = legacy_run["loop_rounds"]
        ss.result = legacy_run["result"]
        ss.console_output = legacy_run["console_output"]
        if legacy_run["status"] != "running":
            ss.running = False
            ss.crew_thread = None

    def draw_crews(self):
        if 'crews' not in ss or not ss.crews:
            st.write(t("crew_run.no_crews"))
            ss.selected_crew_name = None  # Reset selected crew name if there are no crews
            return

        # Check if the selected crew name still exists
        if ss.selected_crew_name not in [crew.name for crew in ss.crews]:
            ss.selected_crew_name = None

        selected_crew_name = st.selectbox(
            label=t("crew_run.select_crew"),
            options=[crew.name for crew in ss.crews],
            index=0 if ss.selected_crew_name is None else [crew.name for crew in ss.crews].index(ss.selected_crew_name) if ss.selected_crew_name in [crew.name for crew in ss.crews] else 0,
        )

        if selected_crew_name != ss.selected_crew_name:
            ss.selected_crew_name = selected_crew_name
            st.rerun()

        selected_crew = self.get_mycrew_by_name(ss.selected_crew_name)

        if selected_crew:
            self.draw_cockpit_header(selected_crew)

            left, right = st.columns([1.05, 0.95], gap="large")
            with left:
                self.draw_panel_header(t("crew_run.configuration_panel"), t("crew_run.configuration_panel_caption"))
                selected_crew.draw(expanded=False,buttons=False)
                self.draw_placeholders(selected_crew)
            
            with right:
                self.draw_panel_header(t("crew_run.execution_panel"), t("crew_run.execution_panel_caption"))
                self.draw_running_lock_notice()
                if not selected_crew.is_valid(show_warning=True):
                    st.error(t("crew.not_valid"))
                loop_config_valid = self.draw_loop_controls(selected_crew)
                self.control_buttons(selected_crew, loop_config_valid=loop_config_valid)

    def control_buttons(self, selected_crew, loop_config_valid=True):
        run_clicked = st.button(
            t('crew_run.run_button'),
            disabled=not selected_crew.is_valid() or not loop_config_valid,
            type="primary",
            use_container_width=True,
        )

        if run_clicked:
            inputs = self.current_inputs()
            loop_config = self.build_loop_config()
            self.start_run(selected_crew, inputs, loop_config)
            st.rerun()

    def start_run(self, selected_crew, inputs, loop_config):
        try:
            crew_snapshot = copy.deepcopy(selected_crew)
        except Exception:
            crew_snapshot = selected_crew

        run_id = f"RUN_{rnd_id()}"
        run_queue = queue.Queue()
        stop_event = threading.Event()
        run_state = {
            "id": run_id,
            "crew_name": selected_crew.name,
            "crew_snapshot": crew_snapshot,
            "inputs": dict(inputs),
            "loop_config": loop_config,
            "queue": run_queue,
            "stop_event": stop_event,
            "thread": None,
            "status": "running",
            "result": None,
            "loop_rounds": [],
            "console_output": [t("crew_run.run_started_log")],
            "started_at": time.strftime("%H:%M:%S"),
            "finished_at": "",
            "saved_result_hashes": set(),
        }

        if loop_config.enabled:
            thread = threading.Thread(
                target=self.run_crew_loop_thread,
                kwargs={
                    "selected_crew": crew_snapshot,
                    "inputs": dict(inputs),
                    "loop_config": loop_config,
                    "message_queue": run_queue,
                    "stop_event": stop_event,
                },
                daemon=True,
            )
        else:
            thread = threading.Thread(
                target=self.run_crew_snapshot_thread,
                kwargs={
                    "selected_crew": crew_snapshot,
                    "inputs": dict(inputs),
                    "message_queue": run_queue,
                },
                daemon=True,
            )

        run_state["thread"] = thread
        ss.crew_runs[run_id] = run_state
        ss.crew_run_order.append(run_id)
        ss.result = None
        ss.loop_rounds = []
        ss.loop_stop_event = stop_event
        thread.start()
        self.sync_running_flag()

    def stop_run(self, run_state):
        if run_state.get("status") != "running":
            return
        stop_event = run_state.get("stop_event")
        if stop_event is not None:
            stop_event.set()
        self.force_stop_thread(run_state.get("thread"))
        self.append_run_log(run_state, t("crew_run.run_stopped_log"))
        self.finish_run(run_state, "stopped")

    def serialize_result(self, result, crew=None) -> str | dict :
        """
        Serialize the crew result for database storage.
        """
        if isinstance(result, dict):
            serialized = {}
            for key, value in result.items():
                if hasattr(value, 'raw'):
                    serialized[key] = {
                        'raw': value.raw,
                        'type': 'CrewOutput'
                    }

                    tasks_output_key = 'tasks_output'
                    if hasattr(value, tasks_output_key):
                        serialized[tasks_output_key] = self.get_tasks_output(
                            value.tasks_output,
                            crew.tasks if crew else None
                        )
                elif hasattr(value, '__dict__'):
                    serialized[key] = {
                        'data': value.__dict__,
                        'type': value.__class__.__name__
                    }
                else:
                    serialized[key] = value
            return serialized
        return str(result)

    def poll_run_queue(self):
        if not (ss.running and ss.crew_thread is not None):
            return
        try:
            message = ss.message_queue.get_nowait()
        except queue.Empty:
            return

        if isinstance(message, dict) and str(message.get("type", "")).startswith("loop_"):
            self.apply_loop_queue_message(message)
            return

        if isinstance(message, dict):
            ss.result = {"result": message.get("result")} if message.get("type") == "run_complete" else message
        else:
            ss.result = {"result": message}
        ss.running = False
        ss.crew_thread = None

    def poll_run_queues(self):
        for run_id in list(ss.get("crew_run_order", [])):
            run_state = ss.crew_runs.get(run_id)
            if not run_state:
                continue
            run_queue = run_state.get("queue")
            if run_queue is None:
                continue

            while True:
                try:
                    message = run_queue.get_nowait()
                except queue.Empty:
                    break

                if isinstance(message, dict):
                    self.apply_run_queue_message(run_state, message)
                else:
                    self.apply_run_queue_message(run_state, {"type": "run_complete", "result": message})
                self.persist_run_result_if_needed(run_state)

        self.sync_running_flag()

    def persist_run_result_if_needed(self, run_state):
        result_payload = run_state.get("result")
        if not isinstance(result_payload, dict):
            return

        result_identifier = str(hash(str(result_payload)))
        saved_hashes = run_state.setdefault("saved_result_hashes", set())
        if result_identifier in saved_hashes:
            return

        from result import Result

        crew_snapshot = run_state.get("crew_snapshot")
        stored_inputs = dict(run_state.get("inputs") or {})
        if "loop" in result_payload:
            stored_inputs = result_payload["loop"].get("round_input", stored_inputs)

        result = Result(
            id=f"R_{rnd_id()}",
            crew_id=run_state.get("crew_name"),
            crew_name=run_state.get("crew_name"),
            inputs=stored_inputs,
            result=self.serialize_result(result_payload, crew_snapshot),
        )

        save_result(result)
        if 'results' not in ss:
            ss.results = []
        ss.results.append(result)
        saved_hashes.add(result_identifier)

    def draw_run_result(self, run_state):
        result_payload = run_state.get("result")
        if result_payload is None:
            if run_state.get("status") == "running":
                st.info(t("crew_run.running"))
            return

        if not isinstance(result_payload, dict):
            st.error(result_payload)
            return

        formatted_result = format_result(result_payload)
        st.expander(t("crew_run.final_output"), expanded=run_state.get("status") != "running").write(formatted_result)
        st.expander(t("crew_run.full_output"), expanded=False).write(result_payload)

        crew_snapshot = run_state.get("crew_snapshot")
        run_result = result_payload.get("result")
        if hasattr(run_result, "tasks_output"):
            task_list = crew_snapshot.tasks if crew_snapshot else None
            tasks_result = get_tasks_outputs_str(run_result.tasks_output, task_list)
            formatted_tasks_result = format_result(tasks_result)
            st.expander(t("crew_run.tasks_results"), expanded=False).write(formatted_tasks_result)
        else:
            formatted_tasks_result = formatted_result

        printable_inputs = dict(run_state.get("inputs") or {})
        if "loop" in result_payload:
            printable_inputs = result_payload["loop"].get("round_input", printable_inputs)

        html_content = generate_printable_view(
            run_state.get("crew_name"),
            result_payload,
            printable_inputs,
            formatted_result,
        )
        if st.button(t("button.open_printable"), key=f"open_printable_{run_state.get('id')}"):
            js = f"""
            <script>
                var printWindow = window.open('', '_blank');
                printWindow.document.write({html_content!r});
                printWindow.document.close();
            </script>
            """
            st.components.v1.html(js, height=0)

        html_tasks_content = generate_printable_view(
            run_state.get("crew_name"),
            result_payload,
            printable_inputs,
            formatted_tasks_result,
        )
        if st.button(t("button.open_printable_complete"), key=f"open_printable_complete_{run_state.get('id')}"):
            js = f"""
            <script>
                var printWindow = window.open('', '_blank');
                printWindow.document.write({html_tasks_content!r});
                printWindow.document.close();
            </script>
            """
            st.components.v1.html(js, height=0)

    def run_card_title(self, run_state):
        status = run_state.get("status", "running")
        started_at = run_state.get("started_at") or "-"
        finished_at = run_state.get("finished_at")
        time_range = f"{started_at} -> {finished_at}" if finished_at else started_at
        title_parts = [
            str(run_state.get("crew_name") or t("crew_run.run_instances")),
            str(run_state.get("id") or ""),
            self.run_status_label(status),
            time_range,
        ]
        return " | ".join(part for part in title_parts if part)

    def draw_run_cards(self):
        st.markdown(f"#### {t('crew_run.run_instances')}")
        run_ids = [run_id for run_id in ss.get("crew_run_order", []) if run_id in ss.get("crew_runs", {})]
        if not run_ids:
            st.info(t("crew_run.no_run_instances"))
            return

        for run_id in reversed(run_ids):
            run_state = ss.crew_runs[run_id]
            status = run_state.get("status", "running")
            status_label = self.run_status_label(status)
            status_class = f"is-{status}"
            with st.expander(self.run_card_title(run_state), expanded=status == "running"):
                st.markdown(
                    f"""
                    <div class="crew-run-instance-card">
                      <div class="crew-run-instance-header">
                        <div>
                          <div class="crew-run-instance-title">{run_state.get("crew_name")} - {run_id}</div>
                          <div class="crew-run-instance-meta">{t("crew_run.run_started_at")}: {run_state.get("started_at") or "-"}</div>
                        </div>
                        <div class="crew-run-instance-status {status_class}">{status_label}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if run_state.get("finished_at"):
                    st.caption(f'{t("crew_run.run_finished_at")}: {run_state.get("finished_at")}')

                if status == "running":
                    if st.button(t("crew_run.stop_this_run"), key=f"stop_run_{run_id}", use_container_width=True):
                        self.stop_run(run_state)
                        st.rerun()

                with st.expander(t("crew_run.run_inputs"), expanded=False):
                    st.json(run_state.get("inputs") or {})

                self.draw_loop_progress(run_state.get("loop_rounds", []))

                with st.expander(t("crew_run.run_log"), expanded=status == "running"):
                    console_text = "\n".join(run_state.get("console_output") or []) or t("crew_run.console_empty")
                    st.markdown('<div class="crew-run-log-panel">', unsafe_allow_html=True)
                    st.code(console_text, language=None)
                    st.markdown('</div>', unsafe_allow_html=True)

                self.draw_run_result(run_state)

    def display_result(self):
        self.poll_run_queues()
        self.draw_run_cards()
        if self.has_running_runs():
            time.sleep(1)
            st.rerun()

    @staticmethod
    def force_stop_thread(thread):
        if not thread or not thread.ident:
            return False
        tid = ctypes.c_long(thread.ident)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))
        if res == 0:
            st.error(t("crew_run.error_stop"))
            return False
        st.success(t("crew_run.success_stop"))
        return True

    def draw(self):
        st.markdown(f"## {self.name}")
        self.draw_crews()
        self.display_result()
