#!/usr/bin/env python3
"""
Groq CLI - Minimalistic REPL Entrypoint
Single entrypoint with interactive REPL loop and slash command routing
"""

import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Confirm
from dotenv import load_dotenv

from assistant import GroqAssistant

# Load environment variables
load_dotenv()

console = Console()


def print_banner():
    """Print minimalistic banner with utilities and usage"""
    banner = Text()
    banner.append("🤖 ", style="bold green")
    banner.append("groq-cli", style="bold cyan")
    banner.append(" - AI Command Assistant\n\n", style="dim")
    
    # Utilities section
    banner.append("🎭 Personas: ", style="bold yellow")
    banner.append("linux • windows • macos • devops • developer • security\n", style="cyan")
    
    banner.append("📁 Files: ", style="bold yellow")
    banner.append("/files • /cd • /read • /write\n", style="cyan")
    
    banner.append("🔧 Tools: ", style="bold yellow")
    banner.append("/apps • /debug • /memory • /clear-memory\n", style="cyan")
    
    banner.append("💬 Usage: ", style="bold yellow")
    banner.append("Type commands naturally or use /slash commands", style="dim")
    
    panel = Panel(
        banner,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)


def get_prompt() -> str:
    """Generate the REPL prompt with current directory"""
    cwd = Path.cwd().name if Path.cwd().name else "/"
    return f"[cyan]groq-cli[/cyan] [dim]{cwd}[/dim] [bold white]❯[/bold white] "


def handle_files_command():
    """List files in current directory with Rich table"""
    try:
        files = os.listdir(".")
        
        table = Table(title="📁 Current Directory Files")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="dim")
        table.add_column("Size", style="green", justify="right")
        
        for item in sorted(files):
            path = Path(item)
            if path.is_dir():
                table.add_row(f"📁 {item}", "directory", "-")
            else:
                try:
                    size = path.stat().st_size
                    size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                    table.add_row(f"📄 {item}", "file", size_str)
                except:
                    table.add_row(f"📄 {item}", "file", "unknown")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing files: {e}[/red]")


def handle_cd_command(path: str):
    """Change current directory"""
    if not path.strip():
        console.print("[red]Usage: /cd <path>[/red]")
        return
        
    try:
        target = Path(path).expanduser().resolve()
        if target.exists() and target.is_dir():
            os.chdir(target)
            console.print(f"[green]Changed to: {target}[/green]")
        else:
            console.print(f"[red]Directory not found: {path}[/red]")
    except Exception as e:
        console.print(f"[red]Error changing directory: {e}[/red]")


def handle_apps_command():
    """List available executables from PATH"""
    try:
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        executables = set()
        
        for path_dir in path_dirs[:10]:  # Limit to first 10 PATH dirs for performance
            try:
                if os.path.isdir(path_dir):
                    for item in os.listdir(path_dir):
                        item_path = os.path.join(path_dir, item)
                        if os.path.isfile(item_path) and os.access(item_path, os.X_OK):
                            executables.add(item)
            except (PermissionError, FileNotFoundError):
                continue
        
        table = Table(title="🚀 Available Commands (from PATH)")
        table.add_column("Executable", style="green")
        
        for exe in sorted(list(executables)[:50]):  # Show top 50
            table.add_row(exe)
        
        console.print(table)
        console.print(f"[dim]Showing first 50 of {len(executables)} available commands[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error listing apps: {e}[/red]")


def handle_read_command(filename: str):
    """Read and display file contents with syntax highlighting"""
    if not filename.strip():
        console.print("[red]Usage: /read <filename>[/red]")
        return
        
    try:
        path = Path(filename)
        if not path.exists():
            console.print(f"[red]File not found: {filename}[/red]")
            return
            
        if not path.is_file():
            console.print(f"[red]Not a file: {filename}[/red]")
            return
            
        # Read file contents
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, 'r', encoding='latin-1') as f:
                content = f.read()
                
        # Determine syntax based on file extension
        suffix = path.suffix.lower()
        syntax_map = {
            '.py': 'python', '.js': 'javascript', '.html': 'html',
            '.css': 'css', '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
            '.xml': 'xml', '.sh': 'bash', '.md': 'markdown',
        }
        
        syntax = Syntax(
            content, 
            syntax_map.get(suffix, 'text'), 
            theme="monokai",
            line_numbers=True,
            word_wrap=True
        )
        
        panel = Panel(
            syntax,
            title=f"📄 {filename}",
            border_style="blue"
        )
        console.print(panel)
        
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")


def handle_write_command(filename: str):
    """Safe write/append to file with confirmation"""
    if not filename.strip():
        console.print("[red]Usage: /write <filename>[/red]")
        return
        
    try:
        path = Path(filename)
        
        # Check if file exists
        if path.exists():
            if not Confirm.ask(f"File '{filename}' exists. Overwrite?", default=False):
                if Confirm.ask("Append to file instead?", default=True):
                    mode = "append"
                else:
                    console.print("[dim]Write cancelled.[/dim]")
                    return
            else:
                mode = "overwrite"
        else:
            mode = "create"
        
        console.print(f"[green]Enter content for '{filename}' (Ctrl+D or Ctrl+Z to finish):[/green]")
        console.print("[dim]Type your content below:[/dim]")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        content = "\n".join(lines)
        
        if mode == "append":
            with open(path, 'a', encoding='utf-8') as f:
                f.write("\n" + content)
            console.print(f"[green]Content appended to '{filename}'[/green]")
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            console.print(f"[green]Content written to '{filename}'[/green]")
            
    except KeyboardInterrupt:
        console.print("\n[dim]Write cancelled.[/dim]")
    except Exception as e:
        console.print(f"[red]Error writing file: {e}[/red]")


def handle_debug_command(assistant: GroqAssistant):
    """Enter debugging mode - send error/code to AI for suggestions"""
    console.print("[yellow]🐛 Debug Mode - Describe your error or paste problematic code[/yellow]")
    console.print("[dim]Type your error message or code (Ctrl+D to finish):[/dim]")
    
    lines = []
    try:
        while True:
            line = input("debug> ")
            if not line.strip():
                break
            lines.append(line)
    except EOFError:
        pass
    except KeyboardInterrupt:
        console.print("\n[dim]Debug cancelled.[/dim]")
        return
    
    if not lines:
        console.print("[dim]No input provided.[/dim]")
        return
    
    debug_input = "\n".join(lines)
    debug_request = f"Debug this error/code and provide solutions: {debug_input}"
    
    console.print("\n[green]🔍 Analyzing debug information...[/green]")
    assistant.process_request(debug_request)


def main():
    """Main REPL loop"""
    print_banner()
    
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        console.print("[red]Error: GROQ_API_KEY environment variable not set[/red]")
        console.print("[dim]Set your API key: export GROQ_API_KEY=your_key_here[/dim]")
        sys.exit(1)
    
    # Initialize assistant
    try:
        assistant = GroqAssistant(api_key)
        console.print(f"[green]✅ Connected with persona: {assistant.current_persona}[/green]")
    except Exception as e:
        console.print(f"[red]Error initializing assistant: {e}[/red]")
        sys.exit(1)
    
    console.print("[dim]Type your requests or use slash commands. Type '/quit' to exit.[/dim]\n")
    
    # Main REPL loop
    while True:
        try:
            # Get user input with dynamic prompt
            user_input = console.input(get_prompt()).strip()
            
            if not user_input:
                continue
            
            # Handle slash commands
            if user_input.startswith('/'):
                parts = user_input[1:].split(' ', 1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in ['quit', 'exit']:
                    console.print("[dim]Goodbye! 👋[/dim]")
                    break
                elif command == 'persona':
                    if args:
                        success = assistant.switch_persona(args.strip())
                        if success:
                            console.print(f"[green]✅ Switched to persona: {args.strip()}[/green]")
                        else:
                            console.print(f"[red]❌ Unknown persona: {args.strip()}[/red]")
                            console.print(f"[dim]Available: {', '.join(assistant.get_available_personas())}[/dim]")
                    else:
                        console.print(f"[cyan]Current persona: {assistant.current_persona}[/cyan]")
                        console.print(f"[dim]Available: {', '.join(assistant.get_available_personas())}[/dim]")
                elif command == 'files':
                    handle_files_command()
                elif command == 'cd':
                    handle_cd_command(args)
                elif command == 'apps':
                    handle_apps_command()
                elif command == 'read':
                    handle_read_command(args)
                elif command == 'write':
                    handle_write_command(args)
                elif command == 'debug':
                    handle_debug_command(assistant)
                else:
                    console.print(f"[red]Unknown command: /{command}[/red]")
                    console.print("[dim]Available: /quit, /persona, /files, /cd, /apps, /read, /write, /debug[/dim]")
            else:
                # Process AI request
                console.print()
                assistant.process_request(user_input)
                console.print()
                
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye! 👋[/dim]")
            break
        except EOFError:
            console.print("\n[dim]Goodbye! 👋[/dim]")
            break
        except Exception as e:
            console.print(f"\n[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    main()