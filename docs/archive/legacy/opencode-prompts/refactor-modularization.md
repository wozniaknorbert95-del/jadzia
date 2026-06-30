We are in Jadzia-Core project (git branch master, recent commit: 800678d docs(handoff): close Stage 2 session with push confirmation).
- Current status: environment installed, requirements.txt satisfied, initial attempt to run pytest failed due to missing virtual‑env activation; tests directory exists but no test runner has executed yet.
- Your task: Refactor the codebase to modularize the monolithic agent module, add Pydantic type hints, implement dependency injection for external services (Gemini, WooCommerce), and create comprehensive unit tests for each new module.
- Files involved: agent.py, main.py, and any large modules under the repository root.
- Required changes:
  1. Create packages: api/, core/, cli/.
  2. Move relevant classes/functions into appropriate packages and add __init__.py files.
  3. Add Pydantic models in core/models.py for request/response schema definitions.
  4. Refactor endpoint definitions in api/ to use FastAPI Depends for service injection.
  5. Inject external services (Gemini, WooCommerce) via dependency injection.
  6. Add unit tests under tests/unit/ for each relocated class/function, covering normal and edge‑case scenarios.
  7. Ensure each new module achieves at least 80 % test coverage.
- Test expectations: pytest must pass with zero failures; coverage report must show ≥ 80 % per package; ruff and black must report no style issues.
- Verification: Execute `ruff check . --fix`, `black .`, `python -m pytest tests/ -v`, and `pytest --cov=.`; all commands must complete successfully.
- Commit message: "Refactor: modularize codebase, add typing, DI, and unit tests"