import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import shutil
import re
from typing import List, Optional


class GammaApp(tk.Tk):
    """
    Tkinter application that provides RGB gamma control for X11 displays
    using the `xrandr` command-line tool.
    """

    def __init__(self) -> None:
        """
        Initialize the GammaApp window, validate environment requirements,
        detect the active display output, and construct the UI.
        """
        super().__init__()

        self.title("Gamma Controller")
        self.geometry("360x300")
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)

        if not shutil.which("xrandr"):
            messagebox.showerror(
                "Error",
                "xrandr not found.\nThis app requires X11 and xrandr."
            )
            self.destroy()
            return

        self.output_name: Optional[str] = self.detect_output()

        self.style: ttk.Style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(
            "TLabel",
            background="#1e1e1e",
            foreground="#ffffff",
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "TButton",
            background="#333333",
            foreground="#ffffff",
            font=("Segoe UI", 10),
            padding=6
        )

        self.style.map(
            "TButton",
            background=[("active", "#444444")]
        )

        self.red: tk.DoubleVar = tk.DoubleVar(value=1.00)
        self.green: tk.DoubleVar = tk.DoubleVar(value=1.00)
        self.blue: tk.DoubleVar = tk.DoubleVar(value=1.00)

        if self.output_name is not None:
            self._build_ui()

    def detect_output(self) -> Optional[str]:
        """
        Detect connected display outputs using `xrandr`.

        Prefers internal laptop panels (eDP/LVDS) when available.
        Returns the name of the selected output or None if detection fails.
        """
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                ["xrandr"],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to run xrandr.")
            self.destroy()
            return None

        connected: List[str] = []

        for line in result.stdout.splitlines():
            if " connected" in line:
                name: str = line.split()[0]
                connected.append(name)

        if not connected:
            messagebox.showerror(
                "Error",
                "No connected displays detected."
            )
            self.destroy()
            return None

        for name in connected:
            if re.match(r"(eDP|LVDS)", name):
                return name

        return connected[0]

    def _build_ui(self) -> None:
        """
        Build and pack all Tkinter widgets for the application.
        """
        padding = {"padx": 20, "pady": 6}

        ttk.Label(
            self,
            text=f"Output: {self.output_name}"
        ).pack(pady=(10, 12))

        ttk.Label(self, text="Red").pack(**padding)
        self._slider(self.red).pack(fill="x", padx=20)

        ttk.Label(self, text="Green").pack(**padding)
        self._slider(self.green).pack(fill="x", padx=20)

        ttk.Label(self, text="Blue").pack(**padding)
        self._slider(self.blue).pack(fill="x", padx=20)

        ttk.Button(
            self,
            text="Apply Gamma",
            command=self.apply_gamma
        ).pack(pady=18)

    def _slider(self, variable: tk.DoubleVar) -> ttk.Scale:
        """
        Create a horizontal slider bound to a DoubleVar.

        :param variable: Tkinter variable controlling the slider value
        :return: Configured ttk.Scale widget
        """
        return ttk.Scale(
            self,
            from_=0.01,
            to=1.0,
            orient="horizontal",
            variable=variable,
            length=280
        )

    def apply_gamma(self) -> None:
        """
        Apply the current RGB gamma values to the detected display output
        using the xrandr command.
        """
        if self.output_name is None:
            return

        r: str = f"{self.red.get():.2f}"
        g: str = f"{self.green.get():.2f}"
        b: str = f"{self.blue.get():.2f}"

        cmd: List[str] = [
            "xrandr",
            "--output", self.output_name,
            "--gamma", f"{r}:{g}:{b}"
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror(
                "Error",
                f"Failed to apply gamma to {self.output_name}."
            )


if __name__ == "__main__":
    app: GammaApp = GammaApp()
    app.mainloop()

