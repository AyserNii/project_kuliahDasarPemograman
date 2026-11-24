# Goal: Build a Tkinter GUI for SmartStock

## User Request

“gw mau sekarang gw jadi aplikasi gui dong dari project gw ini, dan untuk tampilan guinya seperti di foto ya kurang lebih tapi jangan di kasih profile segala sama notif simpel aja sesuai dengan sistem yang udah gw buat lewat cli sekarang”

The user selected Tkinter and requested the GUI become the default launch mode while keeping the CLI available separately.

## Refined Goal

Turn the existing SmartStock PostgreSQL/CLI project into a usable desktop GUI with Tkinter. Match the reference’s clean inventory dashboard layout with a left navigation sidebar, simple header, summary cards, data tables, and understated colors; do not add user profiles or a notification center. Implement the existing CLI workflows as GUI pages by reusing the current repositories, services, and business logic, and preserve the CLI as an explicit alternate entry point.

## Acceptance Criteria

- [ ] `python main.py` launches the Tkinter desktop GUI, while `python main.py --cli` still launches the existing CLI.
- [ ] The GUI has a dashboard and navigable pages for products, suppliers, transactions, sales, inventory analysis, forecasting, import/export, and reports.
- [ ] Existing CLI workflows are usable from the relevant GUI pages: view/create/update/delete products; view/create suppliers; list and record stock IN/OUT; view and record sales; run and view inventory analysis; run demand forecasting; import/export supported CSV data; and access inventory/reorder reports.
- [ ] GUI actions use the current repository/service/business-logic layer and report success, validation, and database errors clearly without silently swallowing them.
- [ ] The visual layout follows the supplied reference at desktop size: sidebar navigation, simple header, inventory summary cards, useful charts/tables, and restrained color accents. No profile/avatar UI or notification center; simple contextual status messages are acceptable.
- [ ] Add focused automated tests for GUI navigation/entry-point selection and representative page actions using fakes or mocks; tests must not require a live PostgreSQL database or a display server.
- [ ] Update directly related run documentation with GUI and CLI commands. Do not change the database schema.

## Scope Boundaries

**In scope:**
- A Tkinter GUI package organized into an app shell, reusable components, and the requested domain pages.
- A default GUI entry point with an explicit CLI command-line option.
- Reusing existing repositories, services, and calculations; basic search/filter and clear empty/error states where practical.
- GUI behavior and entry-point tests that run headlessly.

**Out of scope:**
- Database schema changes, authentication, user profiles, avatar screens, or a notification center.
- Deleting or cascading historical data to bypass database constraints.
- Replacing or removing the existing CLI and its business logic.
- Adding a new GUI toolkit dependency when Tkinter is sufficient.

## Applicable Project Conventions

**Quality gate command:**
- `.venv\Scripts\python.exe -m unittest discover tests`
- Run focused tests during implementation; the full unittest command is the final project gate.

**Commit convention:**
- No repository-specific commit convention was found. Use conventional commits with the goal-skill role marker (`[B]` for Builder, `[I]` for Inspector).
- Include `Assisted-by:` for goal-agent commits and the repository-required `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer.

**Guidelines:**
- No `AGENTS.md`, `CONSTITUTION.md`, or `.github/guidelines/` files were found.
- Follow `alur.md` for the project’s layered architecture and `.venv\Scripts\python.exe -m unittest discover tests` for its documented test command.

**Rules:**
- Preserve existing behavior and use the repository/service layer rather than duplicating database or business logic in GUI widgets.
- Worktree was already dirty before this goal. Do not stage, modify, discard, or commit unrelated existing changes or generated files.
