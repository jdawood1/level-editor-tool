from __future__ import annotations
import sys
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from editor.models import Level, LevelObject, ObjectType
from editor.core import add_object as core_add_object, remove_object as core_remove_object, export as core_export
from editor.telemetry import log_event

class App(tk.Tk):
    def __init__(self, level_path: Path | None):
        super().__init__()
        self.title("Level Editor (Tk)")
        self.geometry("680x480")
        self.level_path: Path | None = level_path
        self.level: Level | None = None

        # Top bar
        bar = ttk.Frame(self, padding=8)
        bar.pack(fill="x")
        ttk.Button(bar, text="Open…", command=self.open_level_dialog).pack(side="left")
        ttk.Button(bar, text="Export…", command=self.export_dialog).pack(side="left", padx=(8, 0))
        self.info_lbl = ttk.Label(bar, text="No level loaded")
        self.info_lbl.pack(side="right")

        # Center split
        body = ttk.Frame(self, padding=8)
        body.pack(fill="both", expand=True)

        # Objects list
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        ttk.Label(left, text="Objects").pack(anchor="w")
        self.tree = ttk.Treeview(left, columns=("type", "x", "y"), show="headings", selectmode="browse")
        self.tree.heading("type", text="Type")
        self.tree.heading("x", text="X")
        self.tree.heading("y", text="Y")
        self.tree.column("type", width=120)
        self.tree.column("x", width=60, anchor="e")
        self.tree.column("y", width=60, anchor="e")
        self.tree.pack(fill="both", expand=True)

        rm_bar = ttk.Frame(left)
        rm_bar.pack(fill="x", pady=(6, 0))
        ttk.Button(rm_bar, text="Remove Selected", command=self.remove_selected).pack(side="left")

        # Add panel
        right = ttk.LabelFrame(body, text="Add Object", padding=8)
        right.pack(side="right", fill="y")

        ttk.Label(right, text="Type").grid(row=0, column=0, sticky="w")
        self.type_var = tk.StringVar(value="wall")
        self.type_cb = ttk.Combobox(right, textvariable=self.type_var, values=["wall", "spawn", "enemy", "coin", "door"], state="readonly", width=12)
        self.type_cb.grid(row=0, column=1, sticky="w")

        ttk.Label(right, text="X").grid(row=1, column=0, sticky="w")
        self.x_var = tk.IntVar(value=0)
        ttk.Entry(right, textvariable=self.x_var, width=8).grid(row=1, column=1, sticky="w")

        ttk.Label(right, text="Y").grid(row=2, column=0, sticky="w")
        self.y_var = tk.IntVar(value=0)
        ttk.Entry(right, textvariable=self.y_var, width=8).grid(row=2, column=1, sticky="w")

        ttk.Button(right, text="Add", command=self.add_from_form).grid(row=3, column=0, columnspan=2, pady=(8, 0))

        for i in range(2):
            right.grid_columnconfigure(i, weight=1)

        # If started with a level path, open it
        if self.level_path:
            self.load_level(self.level_path)

        log_event("gui_open", 0.0, {})

    # --- IO helpers

    def open_level_dialog(self):
        path = filedialog.askopenfilename(title="Open level JSON", filetypes=[("JSON", "*.json")], initialdir=str(Path.cwd()))
        if not path:
            return
        self.load_level(Path(path))

    def load_level(self, path: Path):
        try:
            data = json.loads(Path(path).read_text())
            self.level = Level(**data)
            self.level_path = Path(path)
            self.refresh_tree()
            self.info_lbl.config(text=f"{self.level.name}  ({self.level.width}x{self.level.height})")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open level:\n{e}")

    def export_dialog(self):
        if not self.level_path:
            messagebox.showwarning("No level", "Open a level first.")
            return
        out = filedialog.asksaveasfilename(title="Export to…", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not out:
            return
        try:
            p = core_export(self.level_path, Path(out))
            messagebox.showinfo("Exported", f"Exported: {p}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    # --- Actions

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if not self.level:
            return
        for idx, obj in enumerate(self.level.objects):
            self.tree.insert("", "end", iid=str(idx), values=(obj.type, obj.x, obj.y))

    def add_from_form(self):
        if not self.level_path:
            messagebox.showwarning("No level", "Open a level first.")
            return
        t = self.type_var.get()
        x = int(self.x_var.get())
        y = int(self.y_var.get())
        try:
            core_add_object(self.level_path, t, x, y)
            # reload to reflect persisted + validated model
            self.load_level(self.level_path)
            log_event("gui_add_object", 0.0, {"type": t, "x": x, "y": y})
        except Exception as e:
            messagebox.showerror("Error", f"Add failed:\n{e}")

    def remove_selected(self):
        if not self.level_path:
            messagebox.showwarning("No level", "Open a level first.")
            return
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        try:
            n = core_remove_object(self.level_path, index=idx)
            if n:
                self.load_level(self.level_path)
                log_event("gui_remove_object", 0.0, {"index": idx})
        except Exception as e:
            messagebox.showerror("Error", f"Remove failed:\n{e}")

def main():
    level_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    app = App(level_path)
    app.mainloop()

if __name__ == "__main__":
    main()
