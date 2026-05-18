from crewai import Crew, Process
import streamlit as st
from utils import rnd_id, fix_columns_width
from streamlit import session_state as ss
from datetime import datetime
from html import escape
from llms import llm_providers_and_models, create_llm
import db_utils
from i18n import t
from edit_form_chrome import draw_editor_header, draw_form_section

class MyCrew:
    def __init__(self, id=None, name=None, agents=None, tasks=None, process=None, cache=None, max_rpm=None, verbose=None, manager_llm=None, manager_agent=None, created_at=None, memory=None, planning=None, planning_llm=None, knowledge_source_ids=None):
        self.id = id or "C_" + rnd_id()
        self.name = name or "Crew 1"
        self.agents = agents or []
        self.tasks = tasks or []
        self.process = process or Process.sequential
        self.verbose = bool(verbose) if verbose is not None else True
        self.manager_llm = manager_llm
        self.manager_agent = manager_agent
        self.memory = memory if memory is not None else False
        self.cache = cache if cache is not None else True
        self.max_rpm = max_rpm or 1000
        self.planning = planning if planning is not None else False
        self.planning_llm = planning_llm
        self.created_at = created_at or datetime.now().isoformat()
        self.knowledge_source_ids = knowledge_source_ids or []
        self.edit_key = f'edit_{self.id}'
        if self.edit_key not in ss:
            ss[self.edit_key] = False
        self.tasks_order_key = f'tasks_order_{self.id}'
        if self.tasks_order_key not in ss:
            ss[self.tasks_order_key] = [task.id for task in self.tasks]

    @property
    def edit(self):
        return ss[self.edit_key]

    @edit.setter
    def edit(self, value):
        ss[self.edit_key] = value

    def get_crewai_crew(self, *args, **kwargs) -> Crew:
        crewai_agents = [agent.get_crewai_agent() for agent in self.agents]

        # Create a dictionary to hold the Task objects
        task_objects = {}

        def create_task(task):
            if task.id in task_objects:
                return task_objects[task.id]

            context_tasks = []
            if task.async_execution or task.context_from_async_tasks_ids or task.context_from_sync_tasks_ids:
                for context_task_id in (task.context_from_async_tasks_ids or []) + (task.context_from_sync_tasks_ids or []):
                    if context_task_id not in task_objects:
                        context_task = next((t for t in self.tasks if t.id == context_task_id), None)
                        if context_task:
                            context_tasks.append(create_task(context_task))
                        else:
                            print(f"Warning: Context task with id {context_task_id} not found for task {task.id}")
                    else:
                        context_tasks.append(task_objects[context_task_id])

            # Only pass context if it's an async task or if specific context is defined
            if task.async_execution or context_tasks:
                crewai_task = task.get_crewai_task(context_from_async_tasks=context_tasks)
            else:
                crewai_task = task.get_crewai_task()

            task_objects[task.id] = crewai_task
            return crewai_task

        # Create all tasks, resolving dependencies recursively
        for task in self.tasks:
            create_task(task)

        # Collect the final list of tasks in the original order
        crewai_tasks = [task_objects[task.id] for task in self.tasks]

        # Add knowledge sources if they exist
        knowledge_sources = []
        if 'knowledge_sources' in ss and self.knowledge_source_ids:
            valid_knowledge_source_ids = []
            
            for ks_id in self.knowledge_source_ids:
                ks = next((k for k in ss.knowledge_sources if k.id == ks_id), None)
                if ks:
                    try:
                        knowledge_sources.append(ks.get_crewai_knowledge_source())
                        valid_knowledge_source_ids.append(ks_id)
                    except Exception as e:
                        print(f"Error loading knowledge source {ks.id}: {str(e)}")
            
            # If any knowledge sources were invalid, update the list
            if len(valid_knowledge_source_ids) != len(self.knowledge_source_ids):
                self.knowledge_source_ids = valid_knowledge_source_ids
                db_utils.save_crew(self)

        # Create the crew with knowledge sources
        if self.manager_llm:
            crew_params = {
                'agents': crewai_agents,
                'tasks': crewai_tasks,
                'cache': self.cache,
                'process': self.process,
                'max_rpm': self.max_rpm,
                'verbose': self.verbose,
                'manager_llm': create_llm(self.manager_llm),
                'memory': self.memory,
                'planning': self.planning,
                'knowledge_sources': knowledge_sources if knowledge_sources else None,
            }
            if self.planning and self.planning_llm:
                crew_params['planning_llm'] = create_llm(self.planning_llm)
            crew_params.update(kwargs)
            return Crew(*args, **crew_params)
        elif self.manager_agent:
            crew_params = {
                'agents': crewai_agents,
                'tasks': crewai_tasks,
                'cache': self.cache,
                'process': self.process,
                'max_rpm': self.max_rpm,
                'verbose': self.verbose,
                'manager_agent': self.manager_agent.get_crewai_agent(),
                'memory': self.memory,
                'planning': self.planning,
                'knowledge_sources': knowledge_sources if knowledge_sources else None,
            }
            if self.planning and self.planning_llm:
                crew_params['planning_llm'] = create_llm(self.planning_llm)
            crew_params.update(kwargs)
            return Crew(*args, **crew_params)
        
        crew_params = {
            'agents': crewai_agents,
            'tasks': crewai_tasks,
            'cache': self.cache,
            'process': self.process,
            'max_rpm': self.max_rpm,
            'verbose': self.verbose,
            'memory': self.memory,
            'planning': self.planning,
            'knowledge_sources': knowledge_sources if knowledge_sources else None,
        }
        if self.planning and self.planning_llm:
            crew_params['planning_llm'] = create_llm(self.planning_llm)
        crew_params.update(kwargs)
        return Crew(*args, **crew_params)
    
    def update_knowledge_sources(self):
        self.knowledge_source_ids = ss[f'knowledge_sources_{self.id}']
        db_utils.save_crew(self)

    def delete(self):
        ss.crews = [crew for crew in ss.crews if crew.id != self.id]
        db_utils.delete_crew(self.id)

    def update_name(self):
        self.name = ss[f'name_{self.id}']
        db_utils.save_crew(self)

    def update_process(self):
        self.process = ss[f'process_{self.id}']
        db_utils.save_crew(self)

    def update_tasks(self):
        selected_tasks_ids = ss[f'tasks_{self.id}']
        self.tasks = [task for task in ss.tasks if task.id in selected_tasks_ids and task.agent.id in [agent.id for agent in self.agents]]
        self.tasks = sorted(self.tasks, key=lambda task: selected_tasks_ids.index(task.id))
        ss[self.tasks_order_key] = selected_tasks_ids
        db_utils.save_crew(self)

    def update_verbose(self):
        self.verbose = ss[f'verbose_{self.id}']
        db_utils.save_crew(self)

    def update_agents(self):
        selected_agents = ss[f'agents_{self.id}']
        self.agents = [agent for agent in ss.agents if agent.role in selected_agents]        
        db_utils.save_crew(self)

    def update_manager_llm(self):
        selected_llm = ss[f'manager_llm_{self.id}']
        self.manager_llm = selected_llm if selected_llm != "None" else None
        if self.manager_llm:
            self.manager_agent = None
        db_utils.save_crew(self)

    def update_manager_agent(self):
        selected_agent_role = ss[f'manager_agent_{self.id}']
        self.manager_agent = next((agent for agent in ss.agents if agent.role == selected_agent_role), None) if selected_agent_role != "None" else None
        if self.manager_agent:
            self.manager_llm = None
        db_utils.save_crew(self)

    def update_memory(self):
        self.memory = ss[f'memory_{self.id}']
        db_utils.save_crew(self)
    
    def update_max_rpm(self):
        self.max_rpm = ss[f'max_rpm_{self.id}']
        db_utils.save_crew(self)

    def update_cache(self):
        self.cache = ss[f'cache_{self.id}']
        db_utils.save_crew(self)

    def update_planning(self):
        self.planning = ss[f'planning_{self.id}']
        db_utils.save_crew(self)

    def update_planning_llm(self):
        selected_llm = ss[f'planning_llm_{self.id}']
        self.planning_llm = selected_llm if selected_llm != "None" else None
        db_utils.save_crew(self)

    def is_valid(self, show_warning=False):
        if len(self.agents) == 0:
            if show_warning:
                st.warning(t('warning.crew_no_agents', name=self.name))
            return False
        if len(self.tasks) == 0:
            if show_warning:
                st.warning(t('warning.crew_no_tasks', name=self.name))
            return False
        if any([not agent.is_valid(show_warning=show_warning) for agent in self.agents]):
            return False
        if any([not task.is_valid(show_warning=show_warning) for task in self.tasks]):
            return False
        if self.process == Process.hierarchical and not (self.manager_llm or self.manager_agent):
            if show_warning:
                st.warning(t('warning.crew_no_manager', name=self.name))
            return False
        if self.planning and not self.planning_llm:
            if show_warning:
                st.warning(t('warning.crew_no_planning_llm', name=self.name))
            return False
        return True

    def validate_manager_llm(self):
        available_models = llm_providers_and_models()
        if self.manager_llm and self.manager_llm not in available_models:
            self.manager_llm = None

    def validate_planning_llm(self):
        available_models = llm_providers_and_models()
        if self.planning_llm and self.planning_llm not in available_models:
            self.planning_llm = None

    def draw(self,expanded=False, buttons=True):
        self.validate_manager_llm()
        self.validate_planning_llm()
        name_key = f"name_{self.id}"
        process_key = f"process_{self.id}"
        verbose_key = f"verbose_{self.id}"
        agents_key = f"agents_{self.id}"
        tasks_key = f"tasks_{self.id}"
        manager_llm_key = f"manager_llm_{self.id}"
        manager_agent_key = f"manager_agent_{self.id}"
        memory_key = f"memory_{self.id}"
        planning_key = f"planning_{self.id}"
        planning_llm_key = f"planning_llm_{self.id}"
        cache_key = f"cache_{self.id}"
        max_rpm_key = f"max_rpm_{self.id}"
        
        if self.edit:
            with st.container(border=True, key=f"crew-editor-shell-{self.id}"):
                process_display = {
                    Process.sequential: t("crew.process_sequential"),
                    Process.hierarchical: t("crew.process_hierarchical")
                }
                draw_editor_header(
                    t("editor.crew_title"),
                    t("editor.crew_subtitle"),
                    process_display.get(self.process, str(self.process)),
                )
                draw_form_section(t("editor.section_identity"), t("editor.crew_identity_desc"))
                col_name, col_process = st.columns([1, 1])
                with col_name:
                    st.text_input(t("crew.name"), value=self.name, key=name_key, on_change=self.update_name)
                with col_process:
                    st.selectbox(
                        t("crew.process"),
                        options=[Process.sequential, Process.hierarchical],
                        index=[Process.sequential, Process.hierarchical].index(self.process),
                        format_func=lambda x: process_display[x],
                        key=process_key,
                        on_change=self.update_process
                    )

                draw_form_section(t("editor.section_assignment"), t("editor.crew_assignment_desc"))
                st.multiselect(t("crew.agents"), options=[agent.role for agent in ss.agents], default=[agent.role for agent in self.agents], key=agents_key, on_change=self.update_agents)
                available_tasks = [task for task in ss.tasks if task.agent and task.agent.id in [agent.id for agent in self.agents]]
                available_task_ids = [task.id for task in available_tasks]
                default_task_ids = [task.id for task in self.tasks if task.id in available_task_ids]
                st.multiselect(t("crew.tasks"), options=available_task_ids, default=default_task_ids, format_func=lambda x: next(task.description for task in ss.tasks if task.id == x), key=tasks_key, on_change=self.update_tasks)

                draw_form_section(t("editor.section_model_behavior"), t("editor.crew_runtime_desc"))
                col_manager_llm, col_manager_agent = st.columns(2)
                with col_manager_llm:
                    st.selectbox(t("crew.manager_llm"), options=["None"] + llm_providers_and_models(), index=0 if self.manager_llm is None else llm_providers_and_models().index(self.manager_llm) + 1, key=manager_llm_key, on_change=self.update_manager_llm, disabled=(self.process != Process.hierarchical))
                with col_manager_agent:
                    st.selectbox(t("crew.manager_agent"), options=["None"] + [agent.role for agent in ss.agents], index=0 if self.manager_agent is None else [agent.role for agent in ss.agents].index(self.manager_agent.role) + 1, key=manager_agent_key, on_change=self.update_manager_agent, disabled=(self.process != Process.hierarchical))
                col_verbose, col_memory, col_cache, col_planning = st.columns(4)
                with col_verbose:
                    st.checkbox(t("crew.verbose"), value=self.verbose, key=verbose_key, on_change=self.update_verbose)
                with col_memory:
                    st.checkbox(t("crew.memory"), value=self.memory, key=memory_key, on_change=self.update_memory)
                with col_cache:
                    st.checkbox(t("crew.cache"), value=self.cache, key=cache_key, on_change=self.update_cache)
                with col_planning:
                    st.checkbox(t("crew.planning"), value=self.planning, key=planning_key, on_change=self.update_planning)
                col_planning_llm, col_rpm = st.columns(2)
                with col_planning_llm:
                    st.selectbox(t("crew.planning_llm"), options=["None"] + llm_providers_and_models(), index=0 if self.planning_llm is None else llm_providers_and_models().index(self.planning_llm) + 1, key=planning_llm_key, on_change=self.update_planning_llm, disabled=not self.planning)
                with col_rpm:
                    st.number_input(t("crew.max_requests"), value=self.max_rpm, key=max_rpm_key, on_change=self.update_max_rpm)
                # for some reason knowledge sources for crews are not working, use the knowledge sources in the agents instead
                # if 'knowledge_sources' in ss and len(ss.knowledge_sources) > 0:
                #     knowledge_source_options = [ks.id for ks in ss.knowledge_sources]
                #     knowledge_source_labels = {ks.id: ks.name for ks in ss.knowledge_sources}
                #     valid_knowledge_sources = [ks_id for ks_id in self.knowledge_source_ids 
                #                             if ks_id in knowledge_source_options]

                #     if len(valid_knowledge_sources) != len(self.knowledge_source_ids):
                #         self.knowledge_source_ids = valid_knowledge_sources
                #         db_utils.save_crew(self)
                #     st.multiselect(
                #         "Knowledge Sources",
                #         options=knowledge_source_options,
                #         default=valid_knowledge_sources,
                #         format_func=lambda x: knowledge_source_labels.get(x, "Unknown"),
                #         key=f"knowledge_sources_{self.id}",
                #         on_change=self.update_knowledge_sources
                #     )

                st.markdown('<div class="studio-editor-actions">', unsafe_allow_html=True)
                col_save, col_cancel = st.columns(2)
                with col_save:
                    st.button(t("button.save"), on_click=self.set_editable, args=(False,), key=rnd_id(), type="primary")
                with col_cancel:
                    st.button(t("button.cancel"), on_click=self.cancel_edit, key=rnd_id())
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            fix_columns_width()
            expander_title = t("crew.title", name=self.name) if self.is_valid() else f"❗ {t('crew.title', name=self.name)}"
            with st.expander(expander_title, expanded=expanded):
                process_display = {
                    Process.sequential: t("crew.process_sequential"),
                    Process.hierarchical: t("crew.process_hierarchical")
                }
                st.markdown(f"**{t('crew.process')}:** {process_display.get(self.process, str(self.process))}")
                if self.process == Process.hierarchical:
                    st.markdown(f"**{t('crew.manager_llm')}:** {self.manager_llm}")
                    st.markdown(f"**{t('crew.manager_agent')}:** {self.manager_agent.role if self.manager_agent else 'None'}")
                st.markdown(f"**{t('crew.verbose')}:** {self.verbose}")
                st.markdown(f"**{t('crew.memory')}:** {self.memory}")
                st.markdown(f"**{t('crew.cache')}:** {self.cache}")
                st.markdown(f"**{t('crew.planning')}:** {self.planning}")
                if self.planning and self.planning_llm:
                    st.markdown(f"**{t('crew.planning_llm')}:** {self.planning_llm}")
                st.markdown(f"**{t('crew.max_requests')}:** {self.max_rpm}")
                st.markdown(f"**{t('crew.tasks_section')}:**")
                for i, task in enumerate([task for task in self.tasks if task.agent and task.agent.id in [agent.id for agent in self.agents]], 1):
                    with st.container(border=True):
                        async_tag = t("crew.async_tag") if task.async_execution else ""
                        st.markdown(f"**{i}.{async_tag}  {task.description}**")
                        st.markdown(f"**{t('task.agent')}:** {task.agent.role if task.agent else 'None'}")
                        tools_list = ", ".join([tool.name for tool in task.agent.tools]) if task.agent else "None"
                        st.markdown(f" **{t('agent.tools')}:** {tools_list}")
                        st.markdown(f" **LLM:** {task.agent.llm_provider_model}")
                if self.knowledge_source_ids and 'knowledge_sources' in ss:
                    source_names = [ks.name for ks in ss.knowledge_sources if ks.id in self.knowledge_source_ids]
                    st.markdown(f"**{t('crew.knowledge_sources')}:** {', '.join(source_names)}")
                if buttons:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.button(t("button.edit"), on_click=self.set_editable, key=rnd_id(), args=(True,))
                    with col2:
                        # Instead of direct delete, open modal for cascade delete handling
                        st.button(t("button.delete"), on_click=self.request_delete_modal, key=rnd_id())
                self.is_valid(show_warning=True)
                # If this crew was selected for deletion, draw the modal here
                if ss.get('delete_crew_target_id') == self.id:
                    self.draw_delete_dialog()

    def set_editable(self, edit):
        self.edit = edit
        self.is_new = False
        db_utils.save_crew(self)

    def cancel_edit(self):
        if getattr(self, 'is_new', False):
            self.delete()
        else:
            self.edit = False
        st.rerun()

    # ---------------------- Deletion & Cascade Handling ----------------------
    def request_delete_modal(self):
        """Flag this crew for deletion and trigger modal display."""
        ss['delete_crew_target_id'] = self.id

    def clear_delete_modal(self):
        if 'delete_crew_target_id' in ss:
            del ss['delete_crew_target_id']

    def analyze_dependencies(self):
        """Analyze agents and tasks belonging to this crew for conflicts.

        Returns:
            dict with keys 'agents' and 'tasks'. Each value is a list of dicts:
            {'obj': <agent|task>, 'conflicts': [str,...]}
        """
        # Other crews
        other_crews = [c for c in ss.crews if c.id != self.id]

        # Map task id -> tasks referencing it as context (across all tasks)
        context_refs = {}
        for t in ss.tasks:
            for ref in (t.context_from_async_tasks_ids or []) + (t.context_from_sync_tasks_ids or []):
                context_refs.setdefault(ref, []).append(t)

        agents_info = []
        for agent in self.agents:
            conflicts = []
            # Used in other crews
            used_in_crews = [c.name for c in other_crews if any(a.id == agent.id for a in c.agents)]
            if used_in_crews:
                conflicts.append(f"Used in other crews: {', '.join(used_in_crews)}")
            # Tasks outside this crew that use the agent
            external_tasks = [t for t in ss.tasks if t.agent and t.agent.id == agent.id and t.id not in [ct.id for ct in self.tasks]]
            if external_tasks:
                conflicts.append("Used in tasks outside this crew: " + ", ".join([t.description[:40] for t in external_tasks]))
            agents_info.append({'obj': agent, 'conflicts': conflicts})

        tasks_info = []
        for task in self.tasks:
            conflicts = []
            # Used in other crews
            used_in_crews = [c.name for c in other_crews if any(t.id == task.id for t in c.tasks)]
            if used_in_crews:
                conflicts.append(f"Shared with other crews: {', '.join(used_in_crews)}")
            # Referenced as context by tasks not being deleted
            ref_tasks = [rt for rt in context_refs.get(task.id, []) if rt.id not in [t.id for t in self.tasks]]
            if ref_tasks:
                conflicts.append("Referenced as context in other tasks: " + ", ".join([rt.description[:40] for rt in ref_tasks]))
            tasks_info.append({'obj': task, 'conflicts': conflicts})

        return {'agents': agents_info, 'tasks': tasks_info}

    def draw_delete_dialog(self):
        deps = self.analyze_dependencies()

        if not hasattr(st, 'dialog'):
            st.error(t("crew.invalid_warning"))
            return

        @st.dialog(t("crew.delete_dialog_title", name=self.name))
        def _dlg():
            st.markdown(
                f"""
                <div class="studio-delete-hero">
                  <div class="studio-delete-warning">!</div>
                  <div>
                    <div class="studio-delete-title">{escape(t('crew.confirm_delete_title'))}</div>
                    <div class="studio-delete-copy">{escape(t('crew.confirm_delete_message'))}</div>
                  </div>
                </div>
                <div class="studio-delete-note">{escape(t('crew.conflict_note'))}</div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="studio-delete-scope">
                  <div class="studio-delete-scope-label">{escape(t('crew.delete_scope_title'))}</div>
                  <div class="studio-delete-scope-name">{escape(self.name)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            def draw_dependency_group(group_key, title, empty_text, label_prefix):
                infos = deps[group_key]
                container_key = "delete-dialog-agents" if group_key == "agents" else "delete-dialog-tasks"
                with st.container(border=True, key=container_key):
                    st.markdown(
                        f"""
                        <div class="studio-delete-group-head">
                          <span>{escape(title)}</span>
                          <span>{len(infos)}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if not infos:
                        st.markdown(
                            f'<div class="studio-delete-empty">{escape(empty_text)}</div>',
                            unsafe_allow_html=True,
                        )
                        return

                    for info in infos:
                        obj = info['obj']
                        conflict = len(info['conflicts']) > 0
                        checkbox_key = f"del_{'agent' if group_key == 'agents' else 'task'}_{obj.id}"
                        item_name = obj.role if group_key == "agents" else obj.description[:80]
                        status = t("crew.delete_conflict") if conflict else t("crew.delete_safe")
                        label = f"{label_prefix}: {item_name} - {status}"
                        default_val = False if conflict else True
                        help_text = " | ".join(info['conflicts']) if conflict else None
                        st.checkbox(
                            label,
                            value=default_val if checkbox_key not in ss else ss[checkbox_key],
                            key=checkbox_key,
                            help=help_text,
                        )

            draw_dependency_group(
                "agents",
                t("crew.agents_section"),
                t("crew.delete_empty_agents"),
                "Agent",
            )
            draw_dependency_group(
                "tasks",
                t("crew.tasks_section"),
                t("crew.delete_empty_tasks"),
                t("task.title"),
            )

            st.markdown('<div class="studio-delete-actions">', unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns([1, 1.35, 1.65])
            with col_a:
                if st.button(t("button.cancel")):
                    self.clear_delete_modal()
                    st.rerun()
            with col_b:
                if st.button(t("button.confirm_delete")):
                    self.delete()
                    self.clear_delete_modal()
                    st.rerun()
            with col_c:
                if st.button(t("button.delete_with_items"), type="primary"):
                    selected_agent_ids = [info['obj'].id for info in deps['agents'] if ss.get(f"del_agent_{info['obj'].id}")]
                    selected_task_ids = [info['obj'].id for info in deps['tasks'] if ss.get(f"del_task_{info['obj'].id}")]
                    if selected_task_ids:
                        ss.tasks = [t for t in ss.tasks if t.id not in selected_task_ids]
                        for crew in ss.crews:
                            original_len = len(crew.tasks)
                            crew.tasks = [t for t in crew.tasks if t.id not in selected_task_ids]
                            if len(crew.tasks) != original_len:
                                db_utils.save_crew(crew)
                        for tid in selected_task_ids:
                            db_utils.delete_task(tid)
                    if selected_agent_ids:
                        ss.agents = [a for a in ss.agents if a.id not in selected_agent_ids]
                        for crew in ss.crews:
                            orig_len = len(crew.agents)
                            crew.agents = [a for a in crew.agents if a.id not in selected_agent_ids]
                            if len(crew.agents) != orig_len:
                                db_utils.save_crew(crew)
                        for task in ss.tasks:
                            if task.agent and task.agent.id in selected_agent_ids:
                                task.agent = None
                                db_utils.save_task(task)
                        for aid in selected_agent_ids:
                            db_utils.delete_agent(aid)
                    self.delete()
                    self.clear_delete_modal()
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        _dlg()
