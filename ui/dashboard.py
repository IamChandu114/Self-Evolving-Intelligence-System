from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover - optional dependency
    go = None

from core.intelligence import CoreIntelligence
from evolution.self_evolver import SelfEvolver
from memory.experience_memory import ExperienceMemory
from ui.dashboard_utils import build_repository_statistics, experiences_to_frame, parse_input_signal

APP_TITLE = "Self-Evolving Intelligence System"
APP_SUBTITLE = "Runtime Adaptive Intelligence Engine"
PIPELINE_STAGES = [
    "Input",
    "Memory Retrieval",
    "Reasoning",
    "Decision",
    "Feedback",
    "Knowledge Update",
    "Adaptive Response",
]


def init_state() -> None:
    if "core" not in st.session_state:
        st.session_state.core = CoreIntelligence()
    if "memory" not in st.session_state:
        st.session_state.memory = ExperienceMemory()
    if "evolver" not in st.session_state:
        st.session_state.evolver = SelfEvolver(st.session_state.memory)
    if "history" not in st.session_state:
        st.session_state.history = []
    if "runtime_log" not in st.session_state:
        st.session_state.runtime_log = []
    if "presentation_mode" not in st.session_state:
        st.session_state.presentation_mode = False
    if "session_started_at" not in st.session_state:
        st.session_state.session_started_at = time.time()
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "memory_query" not in st.session_state:
        st.session_state.memory_query = ""
    if "memory_decision_filter" not in st.session_state:
        st.session_state.memory_decision_filter = "All"
    if "memory_min_confidence" not in st.session_state:
        st.session_state.memory_min_confidence = 0.0
    if "console_level_filter" not in st.session_state:
        st.session_state.console_level_filter = "All"


def append_log(level: str, message: str, duration_ms: float | None = None) -> None:
    st.session_state.runtime_log.insert(
        0,
        {
            "timestamp": time.strftime("%H:%M:%S"),
            "level": level.upper(),
            "message": message,
            "duration_ms": duration_ms,
        },
    )
    st.session_state.runtime_log = st.session_state.runtime_log[:20]


def render_header(stats: dict[str, object]) -> None:
    status_text = "Active" if st.session_state.core else "Idle"
    logo_col, title_col, status_col, mode_col = st.columns([0.8, 3.6, 1.2, 1.2])

    with logo_col:
        st.metric("Project Logo", "AI")
    with title_col:
        st.title(APP_TITLE)
        st.caption(APP_SUBTITLE)
    with status_col:
        st.metric("Current Runtime Status", status_text)
        st.caption(f"Project Version: {stats.get('project_version') or 'Not declared'}")
    with mode_col:
        st.session_state.presentation_mode = st.checkbox(
            "Presentation Mode",
            value=st.session_state.presentation_mode,
            help="Simplify the interface for projector-friendly viewing.",
        )
        st.caption("Cleaner layout and fewer developer details")


def render_kpis() -> None:
    memory = st.session_state.memory
    core = st.session_state.core
    evolver = st.session_state.evolver
    last = st.session_state.last_result or {}

    decision_confidence = last.get("decision_details", {}).get("confidence", core.last_confidence)
    strategy_confidence = round(min(0.99, abs(core.strategy_weight) / (abs(core.strategy_weight) + 1.0)), 4)
    inference_time = last.get("inference_time_ms", 0.0)

    cols = st.columns(6)
    cols[0].metric("Strategy Confidence", f"{strategy_confidence:.3f}")
    cols[1].metric("Memory Size", len(memory.experiences))
    cols[2].metric("Decision Confidence", f"{decision_confidence:.3f}")
    cols[3].metric("Inference Time", f"{inference_time:.2f} ms")
    cols[4].metric("Learning Iterations", len(evolver.evolution_history))
    cols[5].metric("Runtime Status", "Active")


def render_pipeline_content(active_index: int, status_text: str) -> None:
    st.subheader("AI Processing Pipeline")
    st.caption(status_text)
    for idx, stage in enumerate(PIPELINE_STAGES):
        if idx < active_index:
            st.write(f"* {idx + 1}. {stage} (completed)")
        elif idx == active_index:
            st.info(f"{idx + 1}. {stage} - Active")
        else:
            st.write(f"{idx + 1}. {stage}")


def render_pipeline(active_index: int, status_text: str, placeholder=None) -> None:
    if placeholder is None:
        with st.container():
            render_pipeline_content(active_index, status_text)
    else:
        with placeholder.container():
            render_pipeline_content(active_index, status_text)


def make_line_chart(df: pd.DataFrame, x: str, y: str, title: str, x_title: str, y_title: str, color: str) -> None:
    if df.empty or y not in df.columns:
        st.info(f"No data available for {title.lower()}.")
        return

    if go is None:
        st.line_chart(df.set_index(x)[[y]] if x in df.columns else df[[y]])
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x] if x in df.columns else df.index,
            y=df[y],
            mode="lines+markers",
            name=y_title,
            line=dict(color=color, width=3),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        legend_title_text="Legend",
    )
    st.plotly_chart(fig, use_container_width=True)


def make_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, x_title: str, y_title: str, color: str) -> None:
    if df.empty or y not in df.columns:
        st.info(f"No data available for {title.lower()}.")
        return

    if go is None:
        st.bar_chart(df.set_index(x)[[y]] if x in df.columns else df[[y]])
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x], y=df[y], name=y_title, marker_color=color))
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        legend_title_text="Legend",
    )
    st.plotly_chart(fig, use_container_width=True)


def pipeline_view(
    values: list[int],
    window_size: int,
    render_placeholder,
    console_placeholder,
    status_placeholder=None,
    progress_placeholder=None,
):
    core = st.session_state.core
    memory = st.session_state.memory
    evolver = st.session_state.evolver

    start_time = time.perf_counter()
    last_mark = [start_time]
    status = status_placeholder if status_placeholder is not None else st.empty()
    progress = progress_placeholder if progress_placeholder is not None else st.progress(0)
    stage_times: list[tuple[str, float]] = []

    def advance(stage_index: int, text: str, level: str = "INFO") -> None:
        now = time.perf_counter()
        step_duration = round((now - last_mark[0]) * 1000, 2)
        last_mark[0] = now
        stage_times.append((text, step_duration))
        append_log(level, text, step_duration)
        status.info(text)
        progress.progress(min(100, int(((stage_index + 1) / len(PIPELINE_STAGES)) * 100)))
        render_pipeline(stage_index, text, render_placeholder)
        time.sleep(0.02)

    advance(0, "Input received")

    input_sum = sum(values)
    feature_vector = {
        "sum": input_sum,
        "length": len(values),
        "positive_terms": sum(1 for value in values if value > 0),
        "negative_terms": sum(1 for value in values if value < 0),
        "magnitude": sum(abs(value) for value in values),
    }

    advance(1, f"Memory retrieval completed using the last {window_size} experience(s)")
    recent_memories = memory.recent(window_size)

    advance(2, "Reasoning started")
    decision, decision_details = core.decide(values, return_details=True)

    reward = 1 if decision == "Action-A" else -1
    advance(3, f"Decision generated: {decision}")
    advance(4, "Feedback analyzed")

    memory_entry = memory.store(
        values,
        decision,
        reward,
        metadata={
            "confidence": decision_details["confidence"],
            "strategy_weight": decision_details["strategy_weight"],
            "input_sum": input_sum,
            "feature_vector": feature_vector,
            "decision_details": decision_details,
        },
    )

    advance(5, "Knowledge updated")
    evolution_update = evolver.evolve(core, window_size=window_size)
    advance(6, "Adaptive response generated", level="SUCCESS")

    inference_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
    adaptation_score = evolution_update.get("adaptation_score", 0.0) if evolution_update else 0.0
    strategy_confidence = round(min(0.99, abs(core.strategy_weight) / (abs(core.strategy_weight) + 1.0)), 4)

    snapshot = {
        "timestamp": time.strftime("%H:%M:%S"),
        "input": values,
        "decision": decision,
        "reward": reward,
        "strategy_weight": round(core.strategy_weight, 4),
        "decision_confidence": decision_details["confidence"],
        "strategy_confidence": strategy_confidence,
        "adaptation_score": adaptation_score,
        "memory_size": len(memory.experiences),
        "feedback_count": len(memory.experiences),
        "learning_iterations": len(evolver.evolution_history),
        "retrieval_count": memory.retrieval_count,
        "inference_time_ms": inference_time_ms,
        "recent_avg_reward": round(
            sum(item["reward"] for item in recent_memories) / len(recent_memories), 3
        )
        if recent_memories
        else 0.0,
    }

    st.session_state.history.append(snapshot)
    st.session_state.last_result = {
        "input": values,
        "feature_vector": feature_vector,
        "decision_details": decision_details,
        "recent_memories": recent_memories,
        "memory_entry": memory_entry,
        "evolution_update": evolution_update,
        "inference_time_ms": inference_time_ms,
        "stage_times": stage_times,
    }

    progress.progress(100)
    status.success("Pipeline completed")
    console_placeholder.success("Pipeline execution finished and runtime state updated.")
    return snapshot


def decision_output_panel() -> None:
    last = st.session_state.last_result
    core = st.session_state.core

    st.subheader("Decision Output")
    if not last:
        st.info("Run the analysis once to populate the decision output and explainability panels.")
        return

    decision_details = last["decision_details"]
    cols = st.columns(4)
    cols[0].metric("Decision", decision_details["decision"])
    cols[1].metric("Confidence", f"{decision_details['confidence']:.3f}")
    cols[2].metric("Execution Time", f"{last['inference_time_ms']:.2f} ms")
    cols[3].metric("Current Strategy", f"{core.strategy_weight:.3f}")


def explainability_panel() -> None:
    last = st.session_state.last_result

    st.subheader("Decision Explainability")
    if not last:
        st.info("The decision trace appears here after the first analysis run.")
        return

    decision_details = last["decision_details"]
    evolution_update = last["evolution_update"] or {}
    recent_memories = last["recent_memories"]

    st.write("Input Analysis -> Memory Match -> Reasoning -> Decision -> Feedback -> Memory Update")
    st.write(
        f"The core engine computes a weighted sum of the input signal. The weighted score is {decision_details['weighted_score']:.3f}, which produces the decision {decision_details['decision']}."
    )

    with st.expander("Decision Trace", expanded=False):
        st.write("Input Analysis")
        st.dataframe(pd.DataFrame(decision_details["feature_contributions"]), use_container_width=True, hide_index=True)
        st.write("Memory Match")
        if recent_memories:
            st.dataframe(experiences_to_frame(recent_memories), use_container_width=True, hide_index=True)
        else:
            st.info("No prior memory was available for context.")
        st.write("Reasoning")
        st.json(
            {
                "input_sum": decision_details["input_sum"],
                "strategy_weight": decision_details["strategy_weight"],
                "weighted_score": decision_details["weighted_score"],
                "confidence": decision_details["confidence"],
            }
        )
        st.write("Decision")
        st.json(
            {
                "decision": decision_details["decision"],
                "decision_margin": decision_details["decision_margin"],
            }
        )
        st.write("Feedback")
        st.json(
            {
                "reward": last["memory_entry"]["reward"],
                "recent_average_reward": last["evolution_update"].get("avg_reward", 0.0),
            }
        )
        st.write("Memory Update")
        st.json(
            {
                "memory_size": len(st.session_state.memory.experiences),
                "learning_iterations": len(st.session_state.evolver.evolution_history),
                "strategy_delta": evolution_update.get("delta", 0.0),
                "adaptation_reason": evolution_update.get("reason", "No adaptation required."),
            }
        )


def render_memory_dashboard() -> None:
    memory = st.session_state.memory
    df = experiences_to_frame(memory.experiences)
    summary = memory.summary()

    st.subheader("Memory Dashboard")

    control_cols = st.columns([2, 1, 1])
    with control_cols[0]:
        st.session_state.memory_query = st.text_input(
            "Memory Search",
            value=st.session_state.memory_query,
            placeholder="Search by input, decision, reward, confidence, or timestamp",
        )
    with control_cols[1]:
        st.session_state.memory_decision_filter = st.selectbox(
            "Memory Filter",
            ["All", "Action-A", "Action-B"],
            index=["All", "Action-A", "Action-B"].index(st.session_state.memory_decision_filter)
            if st.session_state.memory_decision_filter in ["All", "Action-A", "Action-B"]
            else 0,
        )
    with control_cols[2]:
        st.session_state.memory_min_confidence = st.number_input(
            "Min Confidence",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state.memory_min_confidence),
            step=0.05,
        )

    button_cols = st.columns(3)
    if button_cols[0].button("Clear Memory"):
        memory.reset()
        st.session_state.history = []
        st.session_state.last_result = None
        st.session_state.runtime_log = []
        st.success("Memory cleared and persistence file removed.")
    if button_cols[1].button("Reload Memory"):
        memory.load()
        st.success("Memory reloaded from disk.")
    button_cols[2].download_button(
        "Export Memory",
        data=memory.export_json(),
        file_name="experience_memory.json",
        mime="application/json",
    )

    filtered = memory.experiences
    if st.session_state.memory_query.strip():
        filtered = memory.search(st.session_state.memory_query.strip())
    if st.session_state.memory_decision_filter != "All":
        filtered = [item for item in filtered if item.get("decision") == st.session_state.memory_decision_filter]
    if st.session_state.memory_min_confidence > 0:
        filtered = [
            item
            for item in filtered
            if item.get("confidence") is not None and float(item.get("confidence")) >= st.session_state.memory_min_confidence
        ]

    metric_cols = st.columns(4)
    metric_cols[0].metric("Memory Size", summary["size"])
    metric_cols[1].metric("Retrieval Count", summary["retrieval_count"])
    metric_cols[2].metric("Average Reward", f"{summary['average_reward']:.3f}")
    metric_cols[3].metric("Average Confidence", f"{summary['average_confidence']:.3f}")

    st.write("Recent Memories")
    if filtered:
        filtered_df = experiences_to_frame(filtered)
        visible_cols = [
            column
            for column in ["timestamp", "input", "decision", "reward", "confidence", "strategy_weight"]
            if column in filtered_df.columns
        ]
        st.dataframe(filtered_df[visible_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No memories match the current search and filter settings.")

    st.write("Stored Decisions")
    if not df.empty:
        decision_counts = df.groupby("decision", as_index=False).size()
        decision_counts.columns = ["decision", "count"]
        make_bar_chart(decision_counts, "decision", "count", "Decision Distribution", "Decision", "Count", "#2563eb")
    else:
        st.info("No stored decisions yet.")

    st.write("Feedback History")
    if not df.empty:
        feedback_df = df.copy()
        feedback_df["step"] = range(1, len(feedback_df) + 1)
        feedback_left, feedback_right = st.columns(2)
        with feedback_left:
            make_line_chart(
                feedback_df,
                "step",
                "reward",
                "Reward History",
                "Interaction Step",
                "Reward",
                "#d97706",
            )
        with feedback_right:
            make_line_chart(
                feedback_df,
                "step",
                "confidence",
                "Confidence History",
                "Interaction Step",
                "Confidence",
                "#7c3aed",
            )
    else:
        st.info("Feedback history will appear after the first stored experience.")

    st.write("Memory Growth")
    if not df.empty:
        growth_df = pd.DataFrame({"step": range(1, len(df) + 1), "memory_size": range(1, len(df) + 1)})
        make_line_chart(growth_df, "step", "memory_size", "Memory Growth", "Interaction Step", "Memory Size", "#1d4ed8")
    else:
        st.info("Memory growth will appear after the first interaction.")


def render_console() -> None:
    st.subheader("Runtime Activity Console")
    log_cols = st.columns([1, 1, 1])
    with log_cols[0]:
        st.session_state.console_level_filter = st.selectbox(
            "Filter by Level",
            ["All", "INFO", "SUCCESS", "WARNING", "ERROR"],
            index=["All", "INFO", "SUCCESS", "WARNING", "ERROR"].index(st.session_state.console_level_filter)
            if st.session_state.console_level_filter in ["All", "INFO", "SUCCESS", "WARNING", "ERROR"]
            else 0,
        )
    with log_cols[1]:
        st.metric("Log Entries", len(st.session_state.runtime_log))
    with log_cols[2]:
        last_duration = st.session_state.runtime_log[0]["duration_ms"] if st.session_state.runtime_log else None
        st.metric("Execution Duration", f"{last_duration:.2f} ms" if last_duration is not None else "-")

    with st.expander("Collapsible History", expanded=True):
        logs = st.session_state.runtime_log
        if st.session_state.console_level_filter != "All":
            logs = [entry for entry in logs if entry["level"] == st.session_state.console_level_filter]
        if not logs:
            st.info("No runtime logs match the selected filter.")
            return
        for entry in logs:
            header = f"{entry['timestamp']} | {entry['level']}"
            if entry["duration_ms"] is not None:
                header += f" | {entry['duration_ms']:.2f} ms"
            message = f"{header} - {entry['message']}"
            if entry["level"] == "SUCCESS":
                st.success(message)
            elif entry["level"] == "WARNING":
                st.warning(message)
            elif entry["level"] == "ERROR":
                st.error(message)
            else:
                st.info(message)


def render_analytics() -> None:
    st.subheader("Analytics Dashboard")
    history_df = pd.DataFrame(st.session_state.history)
    memory_df = experiences_to_frame(st.session_state.memory.experiences)

    if history_df.empty:
        st.info("Run at least one analysis to generate analytics.")
        return

    history_df = history_df.copy()
    history_df["step"] = range(1, len(history_df) + 1)

    row1 = st.columns(2)
    with row1[0]:
        make_line_chart(history_df, "step", "memory_size", "Memory Growth", "Interaction Step", "Memory Size", "#2563eb")
    with row1[1]:
        if not memory_df.empty:
            decision_counts = memory_df.groupby("decision", as_index=False).size()
            decision_counts.columns = ["decision", "count"]
            make_bar_chart(decision_counts, "decision", "count", "Decision Distribution", "Decision", "Count", "#0f766e")
        else:
            st.info("Decision distribution will appear after the first stored memory.")

    row2 = st.columns(2)
    with row2[0]:
        make_line_chart(history_df, "step", "strategy_weight", "Strategy Evolution", "Interaction Step", "Strategy Weight", "#7c3aed")
    with row2[1]:
        make_line_chart(history_df, "step", "reward", "Reward History", "Interaction Step", "Reward", "#d97706")

    row3 = st.columns(2)
    with row3[0]:
        make_line_chart(history_df, "step", "inference_time_ms", "Runtime Performance", "Interaction Step", "Inference Time (ms)", "#dc2626")
    with row3[1]:
        make_line_chart(history_df, "step", "adaptation_score", "Feedback Trend", "Interaction Step", "Adaptation Score", "#0f766e")


def render_architecture() -> None:
    st.subheader("System Architecture")
    st.code(
        "\n".join(
            [
                "User",
                "  ->",
                "Input Layer",
                "  ->",
                "Feature Extraction",
                "  ->",
                "Memory Module",
                "  ->",
                "Reasoning Engine",
                "  ->",
                "Evolution Module",
                "  ->",
                "Feedback Module",
                "  ->",
                "Knowledge Store",
                "  ->",
                "Decision Output",
            ]
        ),
        language="text",
    )


def render_project_statistics() -> None:
    stats = build_repository_statistics(PROJECT_ROOT)
    st.subheader("Project Statistics")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Modules", stats["project_modules"])
    metric_cols[1].metric("Python Files", stats["python_files"])
    metric_cols[2].metric("Functions", stats["functions"])
    metric_cols[3].metric("Classes", stats["classes"])

    detail_cols = st.columns(4)
    detail_cols[0].metric("Memory Entries", len(st.session_state.memory.experiences))
    detail_cols[1].metric("Project Version", stats.get("project_version") or "Not declared")
    detail_cols[2].metric("Runtime", stats.get("runtime_python") or "Not declared")
    detail_cols[3].metric("Repository Folders", stats["directories"])

    st.write("Repository Structure")
    st.code(
        "\n".join(
            [
                "core/      Decision logic",
                "memory/    Persistent experience storage",
                "evolution/ Strategy adaptation",
                "ui/        Streamlit dashboard",
                "api/       FastAPI service",
                "main.py    Console example",
            ]
        ),
        language="text",
    )


def footer() -> None:
    st.divider()
    st.caption(
        "GitHub Repository | Live Demo | Documentation | Version 1.0. Metrics and charts are derived from live runtime state only."
    )


def render_input_and_pipeline() -> None:
    pipeline_placeholder = None
    left, right = st.columns([1.05, 1.0], gap="large")

    with left:
        st.subheader("User Input")
        raw_input = st.text_input(
            "Input Parameters",
            value="1, -1, 2",
            help="Enter comma- or space-separated integers.",
        )
        window_size = st.number_input(
            "Recent Memory Window",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
            help="Controls how many recent experiences influence the live evolution step.",
        )
        analyze = st.button("Analyze Signal")
        st.caption("The backend logic remains unchanged. This control only shapes the runtime demo experience.")

    with right:
        pipeline_placeholder = st.empty()
        status_placeholder = st.empty()
        progress_placeholder = st.progress(0)
        render_pipeline(
            active_index=0 if st.session_state.last_result is None else len(PIPELINE_STAGES) - 1,
            status_text="Highlighted step updates while the pipeline runs.",
            placeholder=pipeline_placeholder,
        )

    if analyze:
        try:
            values = parse_input_signal(raw_input)
            if not values:
                st.warning("Please enter at least one integer.")
                return
            console_placeholder = st.empty()
            render_pipeline(0, "Processing started", pipeline_placeholder)
            result = pipeline_view(
                values,
                int(window_size),
                pipeline_placeholder,
                console_placeholder,
                status_placeholder=status_placeholder,
                progress_placeholder=progress_placeholder,
            )
            st.success(f"Decision generated: {result['decision']}")
        except ValueError:
            st.error("Please enter only integers separated by commas or spaces.")


def render_explainability_and_decision() -> None:
    left, right = st.columns([1.0, 1.0], gap="large")
    with left:
        decision_output_panel()
    with right:
        explainability_panel()


def render_memory_and_console() -> None:
    left, right = st.columns([1.0, 1.0], gap="large")
    with left:
        render_memory_dashboard()
    with right:
        render_console()


def main_page() -> None:
    stats = build_repository_statistics(PROJECT_ROOT)
    render_header(stats)
    render_kpis()

    st.divider()
    render_input_and_pipeline()

    st.divider()
    st.subheader("Decision Output and Explainability")
    render_explainability_and_decision()

    st.divider()
    render_memory_and_console()

    st.divider()
    render_analytics()

    st.divider()
    render_architecture()

    st.divider()
    render_project_statistics()
    footer()


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="AI", layout="wide")
    init_state()

    if st.session_state.presentation_mode:
        st.sidebar.caption("Presentation mode is enabled.")
    else:
        st.sidebar.subheader("Developer Controls")
        if st.sidebar.button("Reload Memory From Disk"):
            st.session_state.memory.load()
            st.sidebar.success("Memory reloaded.")
        if st.sidebar.button("Reset Session Memory"):
            st.session_state.memory.reset()
            st.session_state.history = []
            st.session_state.runtime_log = []
            st.session_state.last_result = None
            st.session_state.memory_query = ""
            st.session_state.memory_decision_filter = "All"
            st.session_state.memory_min_confidence = 0.0
            st.session_state.console_level_filter = "All"
            st.sidebar.warning("Session memory reset.")
        st.sidebar.caption(f"Memory file: {st.session_state.memory.storage_path}")

    main_page()


if __name__ == "__main__":
    main()
