from datetime import datetime

import streamlit as st
from streamlit import session_state as ss

from db_utils import delete_result, load_results
from i18n import t
from page_chrome import draw_page_header
from utils import format_result, generate_printable_view, get_tasks_outputs_str, rnd_id


class PageResults:
    def __init__(self):
        self.name = t("page.results")

    def _input_summary(self, inputs):
        input_items = list(inputs.items())
        if len(input_items) == 0:
            return ""
        if len(input_items) == 1:
            key, value = input_items[0]
            return f" | {key}: {value[:30]}" + ("..." if len(value) > 30 else "")

        max_chars = max(40 // len(input_items), 10)
        input_parts = []
        for key, value in input_items:
            if len(value) <= max_chars:
                input_parts.append(f"{key}: {value}")
            else:
                input_parts.append(f"{key}: {value[:max_chars]}...")
        return " | " + " | ".join(input_parts)

    def _formatted_task_result(self, result):
        try:
            tasks_output = result.get("tasks_output", None)
            if not tasks_output:
                return ""
            tasks_output_str = list(map(lambda task: task.get("raw", ""), tasks_output))
            tasks_descriptions = [task.get("description") for task in tasks_output]
            tasks_result = get_tasks_outputs_str(tasks_output_str, tasks_descriptions)
            return format_result(tasks_result)
        except Exception:
            return ""

    def _draw_result(self, result):
        timestamp = datetime.fromisoformat(result.created_at).strftime("%Y-%m-%d %H:%M:%S")
        expander_title = f"{result.crew_name} - {timestamp}{self._input_summary(result.inputs)}"

        with st.expander(expander_title, expanded=False):
            st.markdown(f"#### {t('results.inputs')}")
            for key, value in result.inputs.items():
                st.text_area(key, value, disabled=True, key=rnd_id())

            st.markdown(f"#### {t('results.result')}")
            formatted_result = format_result(result.result)
            formatted_tasks_result = self._formatted_task_result(result.result)

            tab1, tab2, tab3 = st.tabs([t("results.rendered"), t("results.raw"), t("results.rendered_complete")])
            with tab1:
                st.markdown(formatted_result)
            with tab2:
                st.code(formatted_result)
            with tab3:
                st.markdown(formatted_tasks_result)

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(t("button.delete"), key=f"delete_{result.id}"):
                    delete_result(result.id)
                    ss.results.remove(result)
                    st.rerun()
            with col2:
                html_content = generate_printable_view(
                    result.crew_name,
                    result.result,
                    result.inputs,
                    formatted_result,
                    result.created_at,
                )
                if st.button(t("button.open_printable"), key=f"print_{result.id}"):
                    js = f"""
                    <script>
                        var printWindow = window.open('', '_blank');
                        printWindow.document.write({html_content!r});
                        printWindow.document.close();
                    </script>
                    """
                    st.components.v1.html(js, height=0)

                if formatted_tasks_result != "":
                    html_tasks_content = generate_printable_view(
                        result.crew_name,
                        result.result,
                        result.inputs,
                        formatted_tasks_result,
                        result.created_at,
                    )

                    if st.button(t("button.open_printable_complete"), key=f"print_full_{result.id}"):
                        js = f"""
                        <script>
                            var printWindow = window.open('', '_blank');
                            printWindow.document.write({html_tasks_content!r});
                            printWindow.document.close();
                        </script>
                        """
                        st.components.v1.html(js, height=0)

    def draw(self):
        if "results" not in ss:
            ss.results = load_results()

        draw_page_header(
            self.name,
            section=t("nav.run"),
            subtitle=t("results.title"),
            count=len(ss.results),
        )

        with st.container(border=True, key="results-filter-card"):
            col1, col2 = st.columns(2)
            with col1:
                crew_filter = st.multiselect(
                    t("results.filter_by_crew"),
                    options=list(set(result.crew_name for result in ss.results)),
                    default=[],
                    key="crew_filter",
                )
            with col2:
                date_filter = st.date_input(
                    t("results.filter_by_date"),
                    value=None,
                    key="date_filter",
                )

        filtered_results = ss.results
        if crew_filter:
            filtered_results = [result for result in filtered_results if result.crew_name in crew_filter]
        if date_filter:
            filtered_results = [
                result for result in filtered_results
                if datetime.fromisoformat(result.created_at).date() == date_filter
            ]

        filtered_results = sorted(
            filtered_results,
            key=lambda result: datetime.fromisoformat(result.created_at),
            reverse=True,
        )

        with st.container(border=True, key="results-list-card"):
            for result in filtered_results:
                self._draw_result(result)
