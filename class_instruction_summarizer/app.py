from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from class_instruction_summarizer.summarizer import summarize_instructions


APP_TITLE = "Class Instruction Condenser"
LOG_DIR = Path.home() / "AppData" / "Local" / "ClassInstructionCondenser" / "logs"
LOG_FILE = LOG_DIR / "app.log"


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


class InstructionSummarizerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x760")
        self.minsize(980, 620)
        self.configure(bg="#f5f7fb")
        self.last_markdown = ""

        self._configure_styles()
        self._build_layout()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f7fb")
        style.configure("Header.TLabel", background="#f5f7fb", foreground="#1f2937", font=("Segoe UI", 18, "bold"))
        style.configure("Subtle.TLabel", background="#f5f7fb", foreground="#475569", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.configure("TLabelframe", background="#f5f7fb", bordercolor="#cbd5e1")
        style.configure("TLabelframe.Label", background="#f5f7fb", foreground="#334155", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(root)
        header.pack(fill=tk.X, pady=(0, 14))
        ttk.Label(header, text=APP_TITLE, style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Paste assignment instructions, then generate a cleaner summary with requirements separated into checklist sections.",
            style="Subtle.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

        body = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True)

        left = ttk.Labelframe(body, text="Original Instructions", padding=10)
        right = ttk.Labelframe(body, text="Condensed Summary", padding=10)
        body.add(left, weight=1)
        body.add(right, weight=1)

        self.input_text = self._scrolled_text(left)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        self.output_text = self._scrolled_text(right)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.configure(state=tk.DISABLED)

        controls = ttk.Frame(root)
        controls.pack(fill=tk.X, pady=(14, 0))

        ttk.Button(controls, text="Condense", style="Primary.TButton", command=self.condense).pack(side=tk.LEFT)
        ttk.Button(controls, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(controls, text="Copy Summary", command=self.copy_summary).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(controls, text="Export Markdown", command=lambda: self.export_summary(".md")).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(controls, text="Export Text", command=lambda: self.export_summary(".txt")).pack(side=tk.LEFT, padx=(8, 0))

        self.status = tk.StringVar(value="Ready")
        ttk.Label(controls, textvariable=self.status, style="Subtle.TLabel").pack(side=tk.RIGHT)

    def _scrolled_text(self, parent: ttk.Frame) -> tk.Text:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        text = tk.Text(
            frame,
            wrap=tk.WORD,
            undo=True,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#111827",
            insertbackground="#111827",
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        return text

    def condense(self) -> None:
        try:
            raw = self.input_text.get("1.0", tk.END).strip()
            result = summarize_instructions(raw)
            self.last_markdown = result.to_markdown()
            self._set_output(self.last_markdown)
            logging.info("Condensed instructions with %s input characters", len(raw))
            self.status.set(f"Condensed at {datetime.now().strftime('%I:%M %p')}")
        except Exception:
            logging.exception("Failed to condense instructions")
            messagebox.showerror(APP_TITLE, f"Something went wrong. Details were logged to:\n{LOG_FILE}")
            self.status.set("Condense failed")

    def clear_all(self) -> None:
        self.input_text.delete("1.0", tk.END)
        self.last_markdown = ""
        self._set_output("")
        self.status.set("Cleared")

    def copy_summary(self) -> None:
        summary = self.output_text.get("1.0", tk.END).strip()
        if not summary:
            messagebox.showinfo(APP_TITLE, "Generate a summary first.")
            return
        self.clipboard_clear()
        self.clipboard_append(summary)
        self.status.set("Summary copied to clipboard")

    def export_summary(self, extension: str) -> None:
        summary = self.output_text.get("1.0", tk.END).strip()
        if not summary:
            messagebox.showinfo(APP_TITLE, "Generate a summary before exporting.")
            return

        default_name = f"class-instructions-summary-{datetime.now().strftime('%Y%m%d-%H%M')}{extension}"
        file_path = filedialog.asksaveasfilename(
            title="Export summary",
            defaultextension=extension,
            initialfile=default_name,
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All Files", "*.*")],
        )
        if not file_path:
            return

        try:
            Path(file_path).write_text(summary + "\n", encoding="utf-8")
            logging.info("Exported summary to %s", file_path)
            self.status.set(f"Saved {Path(file_path).name}")
        except OSError:
            logging.exception("Failed to export summary to %s", file_path)
            messagebox.showerror(APP_TITLE, f"Could not save the summary. Details were logged to:\n{LOG_FILE}")
            self.status.set("Export failed")

    def _set_output(self, value: str) -> None:
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", value)
        self.output_text.configure(state=tk.DISABLED)


def main() -> None:
    configure_logging()
    app = InstructionSummarizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
