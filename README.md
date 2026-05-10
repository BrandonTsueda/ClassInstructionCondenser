# Class Instruction Condenser

Class Instruction Condenser is a small Windows desktop tool for turning pasted class assignment instructions into a cleaner summary with requirement checklists, due-date clues, submission details, citation and formatting notes, and questions to confirm.

It runs locally and does not send class content to an external AI service.

## Why It Matters

Long assignment pages often mix grading requirements, submission instructions, formatting rules, and background context. This app turns that into a practical checklist so the user can start the work with fewer missed requirements.

## Features

- Local rule-based summarization.
- Deliverable and requirement checklist extraction.
- Due-date, citation, and formatting clue detection.
- Questions-to-confirm section for ambiguous instructions.
- Windows executable build flow.
- Local logging under `%LOCALAPPDATA%`.

## Run From Source

```powershell
cd C:\dev\Repos\ClassInstructionCondenser
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m class_instruction_summarizer
```

## Build The Executable

```powershell
cd C:\dev\Repos\ClassInstructionCondenser
powershell -ExecutionPolicy Bypass -File .\build_class_instruction_condenser.ps1 -Clean
```

The executable is created at:

```text
C:\dev\Repos\ClassInstructionCondenser\dist\ClassInstructionCondenser\ClassInstructionCondenser.exe
```

## Test

```powershell
cd C:\dev\Repos\ClassInstructionCondenser
python -m unittest discover -s tests
```

## Notes

- This is a rule-based summarizer, not a grading engine.
- Always compare the generated checklist against the original assignment before submitting work.
- App logs are written to `%LOCALAPPDATA%\ClassInstructionCondenser\logs\app.log`.

## Portfolio Notes

- Demonstrates desktop app packaging, local-first privacy, and testable parsing logic.
- Useful for business intelligence coursework and any repeatable academic workflow.
- Designed to be improved incrementally with document import, export, and optional local AI summarization.
