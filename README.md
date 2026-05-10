# Class Instruction Condenser

Class Instruction Condenser is a small Windows desktop tool for turning pasted class assignment instructions into a cleaner summary with requirement checklists, due-date clues, submission details, citation and formatting notes, and questions to confirm.

It runs locally and does not send class content to an external AI service.

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
