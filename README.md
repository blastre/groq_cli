# 🤖 Groq CLI - AI Command Assistant
> Transform natural language into shell commands with AI-powered assistance

A minimalistic command-line assistant that understands what you want to do and suggests the right commands. Powered by Groq's lightning-fast LLM inference.

## ✨ Features

- **🎭 Expert Personas**: Linux, Windows, macOS, DevOps, Developer, Security specialists
- **🧠 Smart Memory**: Contextual conversations with command history tracking
- **⚡ Lightning Fast**: Groq's optimized inference for instant responses
- **🛡️ Risk Assessment**: Color-coded safety warnings for dangerous commands
- **📁 File Operations**: Built-in file browser, reader, and editor
- **🎨 Rich UI**: Beautiful terminal interface with syntax highlighting

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Groq API key
export GROQ_API_KEY="your_groq_api_key_here"

# Run the CLI
python cli.py
```

Get your free API key from [console.groq.com](https://console.groq.com/keys)

## 💬 Usage Examples

```bash
groq-cli ~/project ❯ find all python files larger than 1MB
# AI suggests: find . -name "*.py" -size +1M -type f

groq-cli ~/project ❯ /persona devops
# ✅ Switched to persona: devops

groq-cli ~/project ❯ create docker container for this app
# AI suggests: docker build -t myapp . && docker run -p 8000:8000 myapp

groq-cli ~/project ❯ /files
# 📁 Shows rich table of current directory files
```

## 🔧 Commands

### Natural Language
Just type what you want to do:
- `compress all log files`
- `check system resources`  
- `find files modified today`
- `backup this directory`

### Slash Commands
- `/persona <name>` - Switch AI persona (linux/windows/macos/devops/developer/security)
- `/files` - List directory contents
- `/read <file>` - View file with syntax highlighting
- `/write <file>` - Create/edit files interactively
- `/cd <path>` - Change directory
- `/apps` - List available commands
- `/debug` - AI-powered error analysis
- `/memory` - Show conversation statistics
- `/quit` - Exit

## 🎭 Personas

| Persona | Specializes In |
|---------|---------------|
| **Linux** | System administration, bash scripting, package management |
| **Windows** | CMD, PowerShell, Windows-specific tools |
| **macOS** | Unix commands with macOS conventions |
| **DevOps** | Docker, Kubernetes, CI/CD, infrastructure |
| **Developer** | Git, testing, build tools, development workflow |
| **Security** | Security scanning, hardening, compliance |

## 🧠 Smart Memory System

- **Context Awareness**: Remembers your recent commands and requests
- **Efficient Caching**: Reduces API calls by caching system information
- **Conversation Flow**: Understands follow-up questions and related tasks
- **Performance Optimized**: Smart prompt management for faster responses

## 📦 Architecture

```
groq_cli/
├── cli.py          # REPL interface and command routing
├── assistant.py    # LangChain + Groq integration with memory
├── personas.py     # AI persona definitions
└── requirements.txt
```

## Screenshots
<img width="889" height="584" alt="Screenshot from 2025-09-05 23-32-37" src="https://github.com/user-attachments/assets/1ff6b1a1-b4df-4865-a9b1-e0cee0569d6f" />
<img width="1920" height="1046" alt="Screenshot from 2025-09-05 23-33-56" src="https://github.com/user-attachments/assets/644c3f06-9010-4d37-9d46-8b326017497f" />
<img width="1920" height="1046" alt="Screenshot from 2025-09-05 23-34-38" src="https://github.com/user-attachments/assets/66af5197-9c33-4682-85ce-2ded37fa9caa" />



