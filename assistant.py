#!/usr/bin/env python3
"""
GroqAssistant - AI Assistant with LangChain integration
Handles persona management, command suggestions, and structured responses
"""

import os
import subprocess
import platform
from typing import List, Optional
from pathlib import Path

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm

from personas import PERSONAS


class CommandSuggestion(BaseModel):
    """Structured response model for AI command suggestions"""
    command: str = Field(description="The shell command to execute")
    explanation: str = Field(description="Brief explanation of what the command does")
    risk_level: str = Field(description="Risk level: low, medium, high")
    alternatives: List[str] = Field(default=[], description="Alternative commands if applicable")


class GroqAssistant:
    """Main AI Assistant class with persona management and command suggestions"""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """Initialize the GroqAssistant"""
        self.console = Console()
        self.current_persona = "linux"
        
        # Initialize LangChain components
        self.llm = ChatGroq(
            api_key=api_key,
            model=model,
            temperature=0.1
        )
        
        # Setup output parser
        self.parser = PydanticOutputParser(pydantic_object=CommandSuggestion)
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self._build_system_template()),
            ("human", "{user_request}")
        ])
        
        # Create the chain
        self.chain = self.prompt_template | self.llm | self.parser
    
    def _build_system_template(self) -> str:
        """Build the system prompt template with context variables"""
        return """You are a helpful command-line assistant with the following persona:

{persona}

CURRENT CONTEXT:
- Operating System: {os_info}
- Current Directory: {current_dir}
- Available Tools: {top_commands}

IMPORTANT RULES:
1. Always respond with valid JSON matching the specified format
2. Only suggest safe, appropriate commands for the current environment
3. Set risk_level to "low", "medium", or "high" based on potential impact
4. Provide brief, clear explanations
5. For medium/high risk commands, provide safer alternatives when possible
6. Consider the current working directory and system context
7. If a command needs elevated privileges, mention it in the explanation
8. Use default system applications when possible
9. Be precise and provide the best command for the scenario

{format_instructions}

Examples of risk levels:
- LOW: ls, pwd, cat, echo, cd
- MEDIUM: cp, mv, rm (specific files), chmod (specific files), wget, curl
- HIGH: rm -rf, format, fdisk, system shutdown/reboot commands

Respond only with the JSON object, no additional text."""
    
    def _get_system_context(self) -> dict:
        """Get current system context for the AI"""
        # Get OS info
        os_info = f"{platform.system()} {platform.release()}"
        
        # Get current directory
        current_dir = os.getcwd()
        
        # Get top 10 most common commands from PATH
        top_commands = self._get_top_commands()
        
        return {
            "persona": PERSONAS.get(self.current_persona, PERSONAS["linux"]),
            "os_info": os_info,
            "current_dir": current_dir,
            "top_commands": ", ".join(top_commands),
            "format_instructions": self.parser.get_format_instructions()
        }
    
    def _get_top_commands(self) -> List[str]:
        """Get list of top commonly used commands"""
        common_commands = [
            "ls", "cd", "pwd", "cat", "grep", "find", "cp", "mv", "rm", "mkdir",
            "chmod", "chown", "ps", "top", "kill", "wget", "curl", "git", "nano", "vim"
        ]
        
        # Try to get commands from PATH (abbreviated for performance)
        try:
            path_dirs = os.environ.get("PATH", "").split(os.pathsep)
            available = set()
            
            for path_dir in path_dirs[:5]:  # Check first 5 PATH directories
                try:
                    if os.path.isdir(path_dir):
                        for item in os.listdir(path_dir)[:20]:  # First 20 items per dir
                            if os.access(os.path.join(path_dir, item), os.X_OK):
                                available.add(item)
                except (PermissionError, FileNotFoundError):
                    continue
            
            # Return intersection of common commands and available commands
            return [cmd for cmd in common_commands if cmd in available][:10]
            
        except Exception:
            return common_commands[:10]
    
    def switch_persona(self, persona_name: str) -> bool:
        """Switch to a different persona"""
        if persona_name.lower() in PERSONAS:
            self.current_persona = persona_name.lower()
            # Rebuild the chain with new persona
            self.chain = self.prompt_template | self.llm | self.parser
            return True
        return False
    
    def get_available_personas(self) -> List[str]:
        """Get list of available personas"""
        return list(PERSONAS.keys())
    
    def get_command_suggestion(self, user_request: str) -> Optional[CommandSuggestion]:
        """Get command suggestion from AI with current context"""
        try:
            # Get current system context
            context = self._get_system_context()
            
            # Invoke the chain with context and user request
            result = self.chain.invoke({
                **context,
                "user_request": user_request
            })
            
            return result
            
        except Exception as e:
            self.console.print(f"[red]Error getting AI suggestion: {e}[/red]")
            return None
    
    def display_suggestion(self, suggestion: CommandSuggestion):
        """Display command suggestion with rich formatting"""
        # Risk-based color coding
        risk_colors = {
            "low": "green",
            "medium": "yellow",
            "high": "red"
        }
        risk_color = risk_colors.get(suggestion.risk_level.lower(), "white")
        
        # Build content
        content = Text()
        content.append("💻 Command: ", style="bold")
        content.append(f"{suggestion.command}\n\n", style=f"bold {risk_color}")
        content.append("📝 Explanation: ", style="bold")
        content.append(f"{suggestion.explanation}\n\n", style="white")
        content.append("⚠️  Risk Level: ", style="bold")
        content.append(f"{suggestion.risk_level.upper()}", style=f"bold {risk_color}")
        
        if suggestion.alternatives:
            content.append("\n\n🔄 Alternatives:\n", style="bold")
            for alt in suggestion.alternatives:
                content.append(f"  • {alt}\n", style="cyan")
        
        # Create panel with risk-based styling
        title = f"[bold]{self.current_persona.upper()} Assistant[/bold]"
        panel = Panel(
            content,
            title=title,
            border_style=risk_color,
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def execute_command(self, command: str) -> bool:
        """Execute the suggested command"""
        try:
            self.console.print(f"[dim]🚀 Executing: {command}[/dim]")
            
            # Execute command with real-time output
            result = subprocess.run(
                command,
                shell=True,
                text=True
            )
            
            if result.returncode == 0:
                self.console.print("[green]✅ Command completed successfully[/green]")
                return True
            else:
                self.console.print(f"[yellow]⚠️  Command exited with code {result.returncode}[/yellow]")
                return False
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]🛑 Command interrupted by user[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[red]❌ Error executing command: {e}[/red]")
            return False
    
    def process_request(self, user_request: str) -> bool:
        """Process a user request end-to-end"""
        # Get AI suggestion
        with self.console.status(f"[bold green]🤖 Getting {self.current_persona} suggestion..."):
            suggestion = self.get_command_suggestion(user_request)
        
        if not suggestion:
            self.console.print("[red]❌ Failed to get command suggestion. Please try again.[/red]")
            return False
        
        # Display suggestion
        self.display_suggestion(suggestion)
        
        # Get user confirmation
        try:
            if suggestion.risk_level.lower() == "high":
                self.console.print("\n[red]🚨 HIGH RISK COMMAND DETECTED![/red]")
                self.console.print("[red]This command could potentially harm your system or data.[/red]")
            
            execute = Confirm.ask(
                "\n[bold]Execute this command?[/bold]", 
                default=(suggestion.risk_level.lower() == "low")
            )
            
            if execute:
                return self.execute_command(suggestion.command)
            else:
                self.console.print("[dim]Command not executed.[/dim]")
                return False
                
        except KeyboardInterrupt:
            self.console.print("\n[dim]Cancelled by user.[/dim]")
            return False