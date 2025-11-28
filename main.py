# Created by Zachary Mangiafesto

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
import os
import json
from datetime import datetime

DATA_FILE = "inventory_data.json"
AUDIT_LOG_FILE = "audit_log.txt"

# -------------------- Audit Logging --------------------

def log_action(username, action, part_data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "user": username,
        "timestamp": timestamp,
        "action": action,
        "part": part_data
    }
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

# -------------------- Data Models --------------------

class Part:
    def __init__(self, harris_pn="", manufacturer_pn="", description="", quantity=0, min_threshold=0, max_threshold=100, notes=""):
        self.harris_pn = harris_pn
        self.manufacturer_pn = manufacturer_pn
        self.description = description
        self.quantity = quantity
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self.notes = notes

    def is_low(self):
        return self.quantity < self.min_threshold

    def is_overstocked(self):
        return self.quantity > self.max_threshold

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Part(**data)

class Area:
    def __init__(self, name):
        self.name = name
        self.parts = {}

    def add_part(self, part: Part):
        key = part.harris_pn or part.manufacturer_pn
        if key:
            self.parts[key] = part

    def remove_part(self, key):
        self.parts.pop(key, None)

    def edit_part(self, key, **kwargs):
        part = self.parts.get(key)
        if part:
            for k, v in kwargs.items():
                setattr(part, k, v)

    def get_low_inventory(self):
        return {k: p for k, p in self.parts.items() if p.is_low()}

    def get_overstocked(self):
        return {k: p for k, p in self.parts.items() if p.is_overstocked()}

    def to_dict(self):
        return {k: p.to_dict() for k, p in self.parts.items()}

    @staticmethod
    def from_dict(name, data):
        area = Area(name)
        for k, part_data in data.items():
            area.parts[k] = Part.from_dict(part_data)
        return area

class InventorySystem:
    def __init__(self):
        self.areas = {}

    def add_area(self, name):
        if name not in self.areas:
            self.areas[name] = Area(name)

    def remove_area(self, name):
        self.areas.pop(name, None)

    def rename_area(self, old_name, new_name):
        if old_name in self.areas and new_name not in self.areas:
            self.areas[new_name] = self.areas.pop(old_name)

    def get_area(self, name):
        return self.areas.get(name)

    def to_dict(self):
        return {name: area.to_dict() for name, area in self.areas.items()}

    def from_dict(self, data):
        for name, area_data in data.items():
            self.areas[name] = Area.from_dict(name, area_data)

    def save_to_file(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_from_file(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.from_dict(data)

inventory = InventorySystem()
inventory.load_from_file()

# -------------------- GUI Application --------------------

class InventoryApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Freedom Inventory Manager")
        self.selected_area = None
        self.filter_mode = tk.StringVar(value="All")

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def setup_ui(self):
        self.area_var = tk.StringVar()
        ttk.Label(self.root, text="Select Area:").grid(row=0, column=0)
        self.area_combo = ttk.Combobox(self.root, textvariable=self.area_var, postcommand=self.update_area_list)
        self.area_combo.grid(row=0, column=1)
        ttk.Button(self.root, text="Manage Areas", command=self.manage_areas).grid(row=0, column=2)

        ttk.Label(self.root, text="Search:").grid(row=1, column=0)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self.root, textvariable=self.search_var)
        search_entry.grid(row=1, column=1)
        search_entry.bind("<KeyRelease>", lambda e: self.load_parts())

        ttk.Label(self.root, text="Filter:").grid(row=1, column=2)
        filter_combo = ttk.Combobox(self.root, textvariable=self.filter_mode, values=["All", "Low Inventory", "Overstocked"], state="readonly")
        filter_combo.grid(row=1, column=3)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_parts())

        self.tree = ttk.Treeview(self.root, columns=("Harris PN", "Manufacturer PN", "Desc", "Qty", "Min", "Max", "Notes"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.grid(row=2, column=0, columnspan=4, sticky="nsew")

        ttk.Button(self.root, text="Add Part", command=self.add_part).grid(row=3, column=0)
        ttk.Button(self.root, text="Edit Part", command=self.edit_part).grid(row=3, column=1)
        ttk.Button(self.root, text="Remove Part", command=self.remove_part).grid(row=3, column=2)

        ttk.Button(self.root, text="Import CSV", command=self.import_csv).grid(row=4, column=0)
        ttk.Button(self.root, text="Export CSV", command=self.export_csv).grid(row=4, column=1)

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)

        self.area_combo.bind("<<ComboboxSelected>>", self.load_parts)

    def update_area_list(self):
        self.area_combo["values"] = list(inventory.areas.keys())

    def load_parts(self, *_):
        area_name = self.area_var.get()
        self.selected_area = inventory.get_area(area_name)
        self.tree.delete(*self.tree.get_children())

        if not self.selected_area:
            return

        search_text = self.search_var.get().lower()
        filter_mode = self.filter_mode.get()

        parts = self.selected_area.parts.values()

        if filter_mode == "Low Inventory":
            parts = filter(lambda p: p.is_low(), parts)
        elif filter_mode == "Overstocked":
            parts = filter(lambda p: p.is_overstocked(), parts)

        for part in parts:
            if (search_text in part.harris_pn.lower() or
                search_text in part.manufacturer_pn.lower() or
                search_text in part.description.lower()):
                self.tree.insert("", "end", iid=part.harris_pn or part.manufacturer_pn, values=(
                    part.harris_pn, part.manufacturer_pn, part.description,
                    part.quantity, part.min_threshold, part.max_threshold, part.notes
                ))

    def manage_areas(self):
        win = tk.Toplevel(self.root)
        win.title("Manage Areas")

        area_listbox = tk.Listbox(win)
        area_listbox.grid(row=0, column=0, columnspan=2)

        for area in inventory.areas.keys():
            area_listbox.insert(tk.END, area)

        def add_area():
            name = simpledialog.askstring("Add Area", "Enter new area name:")
            if name:
                inventory.add_area(name)
                area_listbox.insert(tk.END, name)

        def remove_area():
            selected = area_listbox.curselection()
            if selected:
                name = area_listbox.get(selected)
                inventory.remove_area(name)
                area_listbox.delete(selected)

        def rename_area():
            selected = area_listbox.curselection()
            if selected:
                old_name = area_listbox.get(selected)
                new_name = simpledialog.askstring("Rename Area", f"Rename '{old_name}' to:")
                if new_name:
                    inventory.rename_area(old_name, new_name)
                    area_listbox.delete(selected)
                    area_listbox.insert(tk.END, new_name)

        ttk.Button(win, text="Add", command=add_area).grid(row=1, column=0)
        ttk.Button(win, text="Remove", command=remove_area).grid(row=1, column=1)
        ttk.Button(win, text="Rename", command=rename_area).grid(row=2, column=0, columnspan=2)

    def add_part(self):
        self.part_form("Add Part")

    def edit_part(self):
        selected = self.tree.selection()
        if selected:
            key = selected[0]
            part = self.selected_area.parts.get(key)
            if part:
                self.part_form("Edit Part", part)

    def remove_part(self):
        selected = self.tree.selection()
        if selected:
            key = selected[0]
            removed_part = self.selected_area.parts.get(key)
            if removed_part:
                log_action(self.username, "Remove", removed_part.to_dict())
            self.selected_area.remove_part(key)
            self.load_parts()

    def part_form(self, title, part=None):
        win = tk.Toplevel(self.root)
        win.title(title)

        fields = ["Harris Part Number", "Manufacturer Part Number", "Description", "Quantity", "Min Threshold", "Max Threshold", "Notes"]
        entries = {}

        for i, field in enumerate(fields):
            ttk.Label(win, text=field).grid(row=i, column=0)
            entry = ttk.Entry(win)
            entry.grid(row=i, column=1)
            entries[field] = entry

        if part:
            entries["Harris Part Number"].insert(0, part.harris_pn)
            entries["Manufacturer Part Number"].insert(0, part.manufacturer_pn)
            entries["Description"].insert(0, part.description)
            entries["Quantity"].insert(0, str(part.quantity))
            entries["Min Threshold"].insert(0, str(part.min_threshold))
            entries["Max Threshold"].insert(0, str(part.max_threshold))
            entries["Notes"].insert(0, part.notes)

        def save():
            harris_pn = entries["Harris Part Number"].get()
            manufacturer_pn = entries["Manufacturer Part Number"].get()
            desc = entries["Description"].get()
            qty = int(entries["Quantity"].get())
            min_t = int(entries["Min Threshold"].get())
            max_t = int(entries["Max Threshold"].get())
            notes = entries["Notes"].get()

            key = harris_pn or manufacturer_pn
            new_part = Part(harris_pn, manufacturer_pn, desc, qty, min_t, max_t, notes)
            self.selected_area.add_part(new_part)
            action = "Edit" if part else "Add"
            log_action(self.username, action, new_part.to_dict())
            self.load_parts()
            win.destroy()

        ttk.Button(win, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2)

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path and self.selected_area:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                part = Part(
                    harris_pn=row.get("Harris Part Number", ""),
                    manufacturer_pn=row.get("Manufacturer Part Number", ""),
                    description=row.get("Description", ""),
                    quantity=int(row.get("Quantity", 0)),
                    min_threshold=int(row.get("Min Threshold", 0)),
                    max_threshold=int(row.get("Max Threshold", 100)),
                    notes=row.get("Notes", "")
                )
                self.selected_area.add_part(part)
                log_action(self.username, "Import CSV", part.to_dict())
            self.load_parts()

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv")
        if file_path and self.selected_area:
            data = [part.to_dict() for part in self.selected_area.parts.values()]
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)

    def on_exit(self):
        inventory.save_to_file()
        self.root.destroy()

# -------------------- Launch App --------------------

root = tk.Tk()
username = simpledialog.askstring("Login", "Enter your username:")
if not username:
    messagebox.showerror("Login Failed", "Username is required to continue.")
    root.destroy()
else:
    app = InventoryApp(root, username)
    root.mainloop()

