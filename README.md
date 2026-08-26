# 📋 Clipboard Manager Pro

A powerful Windows clipboard manager that captures and stores everything you copy – text, images, and files – with a modern dark-mode interface. All data persists across system restarts.

---

## ✨ Features

- **Multi‑format Support** – Captures text, images (PNG), and file lists from Explorer
- **Persistent Storage** – History saved in `history.json` and images in `clipboard_data/`; survives reboots
- **Modern Dark UI** – Clean interface built with CustomTkinter
- **Double‑click to Restore** – Copy any previous item back to the clipboard instantly
- **Duplicate Prevention** – Avoids saving identical consecutive entries
- **Item Management** – Delete individual items or clear all history with one click
- **Auto‑save** – Every change is written to disk immediately
- **English Interface** – All labels, messages, and buttons are in English

---

## 📦 Requirements

- **Python 3.6+**
- **Windows OS** (uses `win32clipboard`)
- Dependencies listed in `requirements.txt`

---

## 🚀 Installation & Running

### Option 1 – Run as Python script

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/clipboard-manager-pro.git
cd clipboard-manager-pro

# Install dependencies
pip install -r requirements.txt

# Run the app
python clipboard_manager.py
```

### Option 2 – Quick launch with `.bat` (Windows)

Create a `run.bat` file next to the script with:

```bat
@echo off
python clipboard_manager.py
pause
```

Double‑click `run.bat` to start.

### Option 3 – Standalone `.exe` (no Python needed)

Build a single executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico clipboard_manager.py
```

The `.exe` will be in the `dist/` folder. You can run it on any Windows machine without Python installed.

---

## 🎯 How to Use

1. **Launch the app** – It starts monitoring your clipboard immediately.
2. **Copy anything** – Text, images (from Paint, browser, screenshots), or files (from File Explorer).
3. **View your history** – Every item appears in the list with an icon:
   - 📝 Text  
   - 🖼️ Image  
   - 📁 Files
4. **Restore any item** – Double‑click an entry or select it and click **Copy Selected**.
5. **Manage the list** – Use the **Delete Selected**, **Clear All**, or **Refresh** buttons.
6. **Close the app** – History is automatically saved; nothing is lost.

---

## 📁 Data Storage

- **`history.json`** – Contains the full history (texts, file lists, image references) in JSON format.
- **`clipboard_data/`** – Folder that stores all captured images as `.png` files.

Both are created automatically in the same directory as the application.

---

## 🎨 Customization

- **Change theme** – Edit `ctk.set_appearance_mode("dark")` to `"light"` or `"system"`.
- **Change accent colour** – Replace `"blue"` with `"green"`, `"dark-blue"`, etc.
- **Adjust monitoring speed** – Modify the `self.root.after(500, ...)` value (milliseconds).

---

## 🛠️ Development Notes

- Windows‑only (uses `win32clipboard` for advanced clipboard access).
- Image handling via Pillow (`PIL`).
- UI built with `customtkinter` (modern Tkinter wrapper).
- Text operations use `pyperclip`.

---

## 📄 License

This project is licensed under the **MIT License** – free for personal and commercial use.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ❓ Troubleshooting

**`ModuleNotFoundError: No module named 'pyperclip'`**  
→ Run `pip install pyperclip`

**`ImportError: No module named 'win32clipboard'`**  
→ Run `pip install pywin32`

**Images not being captured?**  
→ Make sure the image is actually in the clipboard (e.g., use Print Screen or copy from Paint). The app only captures when it's running.

**Files not copying back?**  
→ Currently, file lists are copied as text (paths). Full native file‑object support is planned for a future update.

---

## ⭐ Show Your Support

If you find this tool useful, please **star** the repository! ⭐
