import json
import os
import time
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import pyperclip
import win32clipboard
from PIL import ImageGrab, Image
import io
import win32con
import win32file

# CustomTkinter appearance settings
ctk.set_appearance_mode("dark")   # Options: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

class ClipboardManager:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Clipboard Manager Pro")
        self.root.geometry("750x550")
        self.root.resizable(True, True)
        
        # Try to set icon (optional)
        try:
            self.root.iconbitmap("icon.ico")  # If you have an icon file
        except:
            pass

        # Storage directories and files
        self.data_dir = "clipboard_data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.history_file = "history.json"
        self.history = []
        self.last_clip_text = ""
        self.last_clip_hashes = {}

        # Load existing history
        self.load_history()
        
        # Build UI
        self.create_widgets()
        
        # Start monitoring
        self.monitor_clipboard()
        
        # Auto-save on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- Persistent Storage ----------
    def load_history(self):
        """Load history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                if not isinstance(self.history, list):
                    self.history = []
            except:
                self.history = []

    def save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save error: {e}")

    # ---------- UI Construction ----------
    def create_widgets(self):
        """Create all UI elements"""
        # Top frame (title + counter)
        top_frame = ctk.CTkFrame(self.root)
        top_frame.pack(pady=10, padx=15, fill="x")

        self.title_label = ctk.CTkLabel(
            top_frame, 
            text="📋 Clipboard History", 
            font=("Segoe UI", 18, "bold")
        )
        self.title_label.pack(side="left", padx=10)

        self.count_label = ctk.CTkLabel(
            top_frame, 
            text=f"Items: {len(self.history)}", 
            font=("Segoe UI", 13)
        )
        self.count_label.pack(side="right", padx=10)

        # Listbox with scrollbar
        list_frame = ctk.CTkFrame(self.root)
        list_frame.pack(pady=5, padx=15, fill="both", expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 11),
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1f6aa5",
            selectforeground="white",
            relief="flat",
            highlightthickness=0
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Double-click to copy
        self.listbox.bind("<Double-Button-1>", self.copy_selected)

        # Action buttons
        btn_frame = ctk.CTkFrame(self.root)
        btn_frame.pack(pady=10, padx=15, fill="x")

        ctk.CTkButton(
            btn_frame, 
            text="📋 Copy Selected", 
            command=self.copy_selected, 
            width=140
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, 
            text="🗑️ Delete Selected", 
            command=self.delete_selected, 
            width=140, 
            fg_color="#d35b5b"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, 
            text="🧹 Clear All", 
            command=self.clear_all, 
            width=140, 
            fg_color="#6c757d"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, 
            text="🔄 Refresh", 
            command=self.refresh_list, 
            width=140, 
            fg_color="#2b8cbe"
        ).pack(side="left", padx=5)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.root, 
            text="✅ Monitoring clipboard...", 
            font=("Segoe UI", 11), 
            text_color="lightgreen"
        )
        self.status_label.pack(pady=8)

        # Populate list
        self.refresh_list()

    # ---------- List Management ----------
    def refresh_list(self):
        """Refresh the listbox display"""
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(self.history, 1):
            item_type = item.get("type", "text")
            content = item.get("content", "")
            timestamp = item.get("timestamp", "")

            # Display based on type
            if item_type == "text":
                display = f"{idx}. 📝 {content[:55]}{'...' if len(content)>55 else ''}"
            elif item_type == "image":
                fname = os.path.basename(content)
                display = f"{idx}. 🖼️ {fname} (Image)"
            elif item_type == "files":
                file_names = [os.path.basename(p) for p in content]
                display = f"{idx}. 📁 {', '.join(file_names[:3])}{'...' if len(file_names)>3 else ''}"
            else:
                display = f"{idx}. ❓ Unknown"

            self.listbox.insert(tk.END, display)
        self.count_label.configure(text=f"Items: {len(self.history)}")

    def add_item(self, item_type, content):
        """Add a new item to history (avoid duplicates)"""
        # Duplicate prevention
        if item_type == "text":
            if self.history and self.history[-1].get("type") == "text" and self.history[-1].get("content") == content:
                return
        elif item_type == "image":
            # Simple duplicate check for images
            for item in self.history[-5:]:  # Check last 5 items
                if item.get("type") == "image" and item.get("content") == content:
                    return
        elif item_type == "files":
            if self.history and self.history[-1].get("type") == "files" and set(self.history[-1].get("content", [])) == set(content):
                return

        entry = {
            "type": item_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(entry)
        self.save_history()
        self.refresh_list()
        self.status_label.configure(
            text=f"✅ New {item_type} added: {str(content)[:40]}...",
            text_color="lightgreen"
        )
        self.listbox.see(tk.END)

    # ---------- Clipboard Monitoring ----------
    def monitor_clipboard(self):
        """Periodic clipboard check for changes"""
        try:
            # 1. Check for image
            img = self.get_clipboard_image()
            if img:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                img_path = os.path.join(self.data_dir, f"img_{timestamp}.png")
                img.save(img_path, "PNG")
                self.add_item("image", img_path)
                self.root.after(500, self.monitor_clipboard)
                return

            # 2. Check for files
            files = self.get_clipboard_files()
            if files:
                self.add_item("files", files)
                self.root.after(500, self.monitor_clipboard)
                return

            # 3. Check for text
            text = pyperclip.paste()
            if text and text != self.last_clip_text:
                self.last_clip_text = text
                if text.strip() != "":
                    self.add_item("text", text)

        except Exception as e:
            # Silently handle errors to prevent crash
            pass

        # Schedule next check
        self.root.after(500, self.monitor_clipboard)

    # ---------- Windows Clipboard Readers ----------
    def get_clipboard_image(self):
        """Get image from Windows clipboard"""
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                return img
        except:
            pass
        return None

    def get_clipboard_files(self):
        """Get list of files from Windows clipboard"""
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                hdrop = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                files = self._parse_hdrop(hdrop)
                win32clipboard.CloseClipboard()
                return files
            win32clipboard.CloseClipboard()
        except:
            pass
        return None

    def _parse_hdrop(self, hdrop):
        """Parse HDROP structure to file paths"""
        try:
            num_files = win32file.DragQueryFile(hdrop, 0xFFFFFFFF)
            files = []
            for i in range(num_files):
                filename = win32file.DragQueryFile(hdrop, i)
                files.append(filename)
            return files
        except:
            return []

    # ---------- Copy to Clipboard ----------
    def copy_selected(self, event=None):
        """Copy selected item back to clipboard"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select an item first.")
            return
        index = selection[0]
        if index < 0 or index >= len(self.history):
            return

        item = self.history[index]
        item_type = item.get("type")
        content = item.get("content")

        try:
            if item_type == "text":
                pyperclip.copy(content)
                self.status_label.configure(text=f"📋 Text copied (item {index+1})", text_color="lightblue")
            elif item_type == "image":
                if os.path.exists(content):
                    img = Image.open(content)
                    self._copy_image_to_clipboard(img)
                    self.status_label.configure(text=f"🖼️ Image copied (item {index+1})", text_color="lightblue")
                else:
                    messagebox.showerror("Error", "Image file not found.")
            elif item_type == "files":
                self._copy_files_to_clipboard(content)
                self.status_label.configure(text=f"📁 Files copied (item {index+1})", text_color="lightblue")
            else:
                messagebox.showinfo("Info", "Unknown type, cannot copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Copy failed: {str(e)}")

        # Reset status after 2 seconds
        self.root.after(2000, lambda: self.status_label.configure(
            text="✅ Monitoring clipboard...", 
            text_color="lightgreen"
        ))

    def _copy_image_to_clipboard(self, img):
        """Copy PIL image to Windows clipboard (DIB format)"""
        from io import BytesIO
        output = BytesIO()
        img.convert("RGB").save(output, format="BMP")
        data = output.getvalue()[14:]  # Remove BMP header
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, data)
        win32clipboard.CloseClipboard()

    def _copy_files_to_clipboard(self, file_paths):
        """Copy file list to clipboard (as text, fallback method)"""
        # Note: Full HDROP implementation requires more complex code
        # This is a simple fallback that copies paths as text
        pyperclip.copy("\n".join(file_paths))
        self.status_label.configure(
            text="📁 File paths copied as text (full file copy coming soon)", 
            text_color="yellow"
        )

    # ---------- Delete Operations ----------
    def delete_selected(self):
        """Delete selected item from history"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Select an item first.")
            return
        index = selection[0]
        if messagebox.askyesno("Confirm Delete", f"Delete item {index+1}?"):
            item = self.history[index]
            if item.get("type") == "image":
                img_path = item.get("content")
                if os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except:
                        pass
            del self.history[index]
            self.save_history()
            self.refresh_list()
            self.status_label.configure(text="🗑️ Item deleted.", text_color="orange")

    def clear_all(self):
        """Clear all history"""
        if not self.history:
            messagebox.showinfo("Info", "History is already empty.")
            return
        if messagebox.askyesno("Confirm Clear All", "Delete all history? This cannot be undone."):
            for item in self.history:
                if item.get("type") == "image":
                    img_path = item.get("content")
                    if os.path.exists(img_path):
                        try:
                            os.remove(img_path)
                        except:
                            pass
            self.history.clear()
            self.save_history()
            self.refresh_list()
            self.status_label.configure(text="🧹 All history cleared.", text_color="red")

    # ---------- Application Close ----------
    def on_close(self):
        """Save and exit"""
        self.save_history()
        self.root.destroy()

    # ---------- Run ----------
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ClipboardManager()
    app.run()