import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# --- COLOR PALETTE ---
BG_MAIN = "#1e1e1e"  # Deep dark gray
BG_SECONDARY = "#252526"  # Slightly lighter gray for top bar
ACCENT = "#007acc"  # Classic "VS Code" blue
TEXT_COLOR = "#ffffff"  # Pure white
BTN_HOVER = "#1c97ea"  # Lighter blue for hover


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SwayBG Manager")
        self.root.geometry("900x700")
        self.root.configure(bg=BG_MAIN)

        # --- 1. Top Control Bar ---
        self.top_bar = tk.Frame(self.root, bg=BG_SECONDARY, height=60)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(
            False
        )  # Prevents frame from shrinking to button size

        self.folder_button = tk.Button(
            self.top_bar,
            text="Select Wallpaper Folder",
            bg=ACCENT,
            fg=TEXT_COLOR,
            activebackground=BTN_HOVER,
            activeforeground=TEXT_COLOR,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            command=self.select_folder,
        )
        self.folder_button.pack(pady=12)

        # --- 2. The Scrolling Area ---
        # highlightthickness=0 removes the annoying white border around canvases
        self.canvas = tk.Canvas(self.root, bg=BG_MAIN, highlightthickness=0)

        # Modern scrollbar styling is limited in standard Tkinter,
        # but we can at least make it fit the theme.
        self.scrollbar = tk.Scrollbar(
            self.root, orient="vertical", command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_MAIN)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.scrollbar.pack(side="right", fill="y")

        self.thumbnails = []

    def change_wallpaper(self, image_path):
        command = f"swaymsg \"output * bg '{image_path}' fill\""
        try:
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"Error: {e}")

    def render_images(self, image_paths):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.thumbnails.clear()

        max_columns = 4  # Increased columns for a wider look

        for index, path in enumerate(image_paths):
            try:
                img = Image.open(path)
                img.thumbnail((180, 180))  # Slightly smaller for better grid feel
                photo = ImageTk.PhotoImage(img)
                self.thumbnails.append(photo)

                # Style the button to be a flat "card"
                btn = tk.Button(
                    self.scrollable_frame,
                    image=photo,
                    command=lambda p=path: self.change_wallpaper(p),
                    bg=BG_MAIN,
                    activebackground=ACCENT,  # Glow blue when clicked
                    borderwidth=0,
                    cursor="hand2",  # Change cursor to hand on hover
                )

                row = index // max_columns
                col = index % max_columns
                btn.grid(row=row, column=col, padx=10, pady=10)

            except Exception as e:
                print(f"Skipping {path}: {e}")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        images = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(valid_exts)
        ]
        self.render_images(images)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
