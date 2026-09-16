"""
Ziskare AI - Desktop & Operations Agent
=======================================
Autonomous specialist agent for opening files/folders, launching applications,
and executing operating system tasks on the Windows laptop.
"""

from typing import Optional, Any
from ziskare_ai.agents.base import BaseAgent
from ziskare_ai.agents.tools import (
    open_path,
    launch_app,
    find_files,
    list_dir,
    read_file,
    write_file,
    run_command,
    get_system_stats
)

DESKTOP_SYSTEM_PROMPT = (
    "You are the Ziskare Desktop Agent, an autonomous operating system and desktop operations specialist on Windows. "
    "Your specialty is interacting with the laptop desktop, opening files and directories, launching applications, "
    "and executing safe system and workspace operations."
)


class DesktopAgent(BaseAgent):
    """
    Autonomous desktop and laptop operations specialist.
    Capable of opening files and folders, launching desktop apps, and searching files.
    """

    def __init__(self, ai: Optional[Any] = None, silent: bool = False):
        super().__init__(
            name="DesktopAgent",
            role="Desktop & System Operations Specialist",
            system_prompt=DESKTOP_SYSTEM_PROMPT,
            ai=ai,
            tools={
                "open_path": open_path,
                "launch_app": launch_app,
                "find_files": find_files,
                "list_dir": list_dir,
                "read_file": read_file,
                "write_file": write_file,
                "run_command": run_command,
                "get_system_stats": get_system_stats
            },
            temperature=0.2,
            silent=silent
        )

    def open(self, target: str) -> str:
        """Open a file or folder on the laptop."""
        return open_path(target)

    def launch(self, app_name: str) -> str:
        """Launch an application on the laptop."""
        return launch_app(app_name)

    def search(self, query: str, search_dir: Optional[str] = None) -> str:
        """Search for files or folders matching a query."""
        return find_files(query, search_dir=search_dir)

    def execute_task(self, prompt: str) -> str:
        """Autonomously determine the desktop action from user prompt and execute it."""
        import re
        low = prompt.lower()

        # Check launch app
        if any(w in low for w in ["launch", "start app", "open app", "run app", "open notepad", "open calc", "open calculator", "open terminal", "open vs code", "open vscode", "open paint"]):
            app = re.sub(r'^(?:please\s+)?(?:launch|start|open|run)\s+(?:the\s+)?(?:app\s+|application\s+)?', '', prompt, flags=re.IGNORECASE).strip(" .")
            return self.launch(app)

        # Check open recent/latest image
        if any(w in low for w in [
            "recent image", "latest image", "last image", "the image",
            "open image", "show image", "revent image", "revently generated",
            "recently generated", "open the recent image", "open recent", "open the recent"
        ]):
            return self.open("latest image")

        # Check open folder / file
        if any(w in low for w in ["open folder", "open directory", "show in explorer", "open file", "open the file", "open the folder", "open images", "open output", "open downloads"]):
            target = re.sub(r'^(?:please\s+)?(?:open|show)\s+(?:the\s+)?(?:folder\s+|directory\s+|file\s+)?(?:called\s+|named\s+)?', '', prompt, flags=re.IGNORECASE).strip(" .")
            return self.open(target)

        # Check search
        if any(w in low for w in ["find file", "search file", "locate file", "where is"]):
            query = re.sub(r'^(?:please\s+)?(?:find|search|locate|where is)\s+(?:the\s+)?(?:file\s+|folder\s+)?', '', prompt, flags=re.IGNORECASE).strip(" .?")
            return self.search(query)

        # Fallback to open
        if low.startswith("open "):
            target = prompt[5:].strip(" .")
            return self.open(target)

        # Default run
        return self.run(f"Execute this desktop/laptop task: {prompt}")
