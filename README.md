# Self-Evolving Intelligence System

Runtime-adaptive AI research prototype for live academic demonstration.

This project shows a small but honest adaptive loop:

1. A user submits an integer signal.
2. The core engine produces a decision from a weighted sum.
3. The experience is stored in memory.
4. The evolver adjusts strategy using recent feedback.
5. The dashboard explains what happened in real time.

The project does not pretend to be a neural network. It is a rule-based adaptive system with persistence, explainability, analytics, and a presentation-ready Streamlit interface.

## Current Architecture

- `core/` handles the decision rule and strategy updates.
- `memory/` stores and reloads experiences from local JSON storage.
- `evolution/` applies reward-based adaptation.
- `ui/` renders the Streamlit dashboard and UI helpers.
- `api/` exposes the same adaptive loop through FastAPI.

## Existing Features

- Runtime decision engine
- Persistent experience memory
- Feedback-driven strategy evolution
- Explainable decision trace
- Runtime activity console
- Memory search and filtering
- Memory export and reset
- Analytics dashboard
- Architecture visualization
- Project statistics
- Presentation mode
- FastAPI decision endpoint

## Current Workflow

1. User enters a signal such as `1, -1, 2`.
2. The input is parsed into integers.
3. The core calculates a weighted score and decision confidence.
4. Recent memory is retrieved for context.
5. The decision and reward are stored in memory.
6. The evolver updates the strategy weight.
7. The dashboard shows the live result, explanation, and analytics.

## Strengths

- Small, easy to explain codebase
- Clear runtime feedback loop
- Persistent memory improves demo continuity
- Native Streamlit layout is clean and presentation-friendly
- Metrics shown in the UI are derived from actual runtime state

## Weaknesses

- The learning rule is intentionally simple
- The system is not a neural model
- Accuracy and benchmark claims are not applicable
- No automated test suite is included yet

## Recommended Improvements

- Add a small test suite for the decision and memory flow
- Add optional SQLite persistence for larger demos
- Add session export and import
- Add richer reward policies and more decision modes
- Add CI and deployment automation

## How To Run

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the Streamlit dashboard:

```powershell
streamlit run ui/app.py
```

Run the API server:

```powershell
uvicorn api.server:app --reload
```

Run the console demo:

```powershell
python main.py
```

## Folder Structure

```text
core/        Core decision logic
memory/      Persistent experience storage
evolution/   Strategy adaptation
ui/          Streamlit dashboard and helpers
api/         FastAPI service
main.py      Console example
README.md    Project documentation
```

## Screenshots

Screenshots are not bundled in the repository yet. Add them to the project when preparing the final presentation pack.

## Presentation Notes

- Use Presentation Mode for a simpler projector-friendly interface.
- Show the decision trace while explaining the feedback loop.
- Use the memory and analytics tabs to show that the system retains and reuses prior experiences.
- Emphasize that all displayed metrics come from runtime state, not fabricated benchmarks.

## Known Limitations

- Memory is persisted locally as JSON, not in a database.
- The decision engine is intentionally lightweight and rule-based.
- The project is best positioned as a research prototype, not a production AI service.

## Future Work

- Add persistent SQLite storage
- Add unit tests and CI
- Add downloadable session reports
- Add more advanced explanation views
- Add deployment automation for repeatable demos
