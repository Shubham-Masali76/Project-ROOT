# R.O.O.T. (Reactive Operational Orchestration Technology)

R.O.O.T. is a fully autonomous, locally-hosted AI Operating System Assistant designed to act as the central intelligence of your computer. 

Built with advanced neuroplasticity and self-healing algorithms, R.O.O.T. goes beyond simple chatbot interactions. It hooks directly into the Windows operating system to perform tasks, organize files, manage media, and adapt to your personal habits.

## ⚠️ Beta Testing Phase

**R.O.O.T. is currently in Active Beta Testing.**
Because it actively hooks into your file system and OS processes, you may occasionally encounter unexpected behavior. 
If you find any bugs, crashes, or weird behavior, please open an issue in the **[Issues](../../issues)** tab of this repository so we can fix it!

---

## 🌟 Core Architecture

### 1. The Digital Immune System (Auto-Healing)
R.O.O.T. is designed to never die. It features an advanced `immune_system.py` module that wraps around all core threads. If the AI encounters a fatal crash or syntax error, it will autonomously capture the traceback, generate a code patch via the LLM, physically rewrite its own Python source code, and perform a hot-restart to heal itself. 

### 2. Tri-Memory Neuroplasticity
R.O.O.T. possesses a brain-inspired memory architecture to prevent catastrophic forgetting:
- **Short-Term Memory (STM):** A sliding context window of active interactions.
- **Hippocampal Consolidation:** A background thread that periodically analyzes the STM and consolidates important habits and preferences.
- **Long-Term Memory (LTM):** Persistent JSON storage that modifies the AI's core behavior directives over time based on your workflow.

### 3. Over-The-Air Auto-Updates
R.O.O.T. stays fresh automatically. On boot, the `auto_updater.py` module silently pings this repository. If a new commit is detected, R.O.O.T. downloads the fresh codebase, safely overwrites its internal logic (while protecting your API keys and memories), and restarts.

### 4. Interactive Holographic Interface
R.O.O.T. features a custom-built frameless GUI (`gui/face.py`) that floats above your desktop. 
- **Voice or Text:** Speak naturally to the AI, or type commands into the built-in terminal.
- **Stealth Controls:** Double-click the robot face to collapse the terminal. Right-click to pin it to the top of your screen. 
- **Privacy First:** The microphone is muted by default and can be toggled instantly via the `/mic` command.

### 5. 14 Independent Action Operators
R.O.O.T. features a specialized execution queue capable of handling advanced OS-level commands natively:
- **OS Controller:** Manage windows, processes, and applications.
- **Visionary:** Screen analysis and GUI interaction.
- **File Manager:** Deep system file manipulation and download organization.
- **Messenger & Social:** Automate messaging platforms and YouTube controls.
- **System Doctor:** Autonomous deep cleaning and diagnostics.

---

## ⚡ Installation

We have created a powerful compiled bootstrapper to make installation effortless. 

**Do not download the source code manually.**

1. Go to the **Releases** tab on the right side of this page.
2. Download **`ROOT_Setup.exe`**.
3. Double-click the file. 

The Bootstrapper will launch a beautiful setup GUI. It will ask for your Gemini API Key (which never leaves your computer), securely download the brain, build your virtual environment, install all neural dependencies, and inject R.O.O.T. directly into your Windows Startup folder.

---

## 💻 Technologies Used
- **Core Intelligence:** Google Gemini 1.5 Flash (via `google-genai`)
- **Voice & Ears:** `SpeechRecognition`, `pyttsx3`, `vosk`, `edge-tts`
- **Vision & UI Manipulation:** `PyAutoGUI`, `mss`, `Pillow`, `pygetwindow`
- **System Control:** `psutil`, `winshell`, `watchdog`, `shutil`
- **Installation Bootstrapper:** `Tkinter`, `PyInstaller`

---

## 🔒 Privacy & Security

R.O.O.T. operates **entirely locally** on your machine. 
- It uses the Google Gemini API to process intelligence, but your files, screen captures, and long-term memory logs (`memory_ltm.json`) never leave your local hard drive. 
- The `.env` file containing your API key is generated securely on your local machine by the installer and is rigorously protected from updates.

---

## 👨‍💻 Authors & References
- **Author:** Shubham Masali
- **References:** Inspired by neuro-symbolic AI architectures and OS-level deep learning agents.

---

*“I am not a chatbot. I am the Operating System.”*
