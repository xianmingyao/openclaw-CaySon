# Copy of CLI-Anything repl_skin.py for windows-control harness
# Original: https://github.com/HKUDS/CLI-Anything

import os
import sys

# ANSI colors
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_CYAN = "\033[38;5;80m"
_CYAN_BG = "\033[48;5;80m"
_WHITE = "\033[97m"
_GRAY = "\033[38;5;245m"
_DARK_GRAY = "\033[38;5;240m"
_LIGHT_GRAY = "\033[38;5;250m"
_ACCENT = "\033[38;5;208m"  # orange accent for Windows
_GREEN = "\033[38;5;78m"
_YELLOW = "\033[38;5;220m"
_RED = "\033[38;5;196m"
_BLUE = "\033[38;5;75m"
_ICON = f"{_CYAN}{_BOLD}◆{_RESET}"
_ICON_SMALL = f"{_CYAN}▸{_RESET}"


def _strip_ansi(text: str) -> str:
    import re
    return re.sub(r"\033\[[^m]*m", "", text)


def _visible_len(text: str) -> int:
    return len(_strip_ansi(text))


class ReplSkin:
    """REPL skin for cli-anything-windows-control."""

    def __init__(self, software: str, version: str = "1.0.0", history_file: str = None):
        self.software = software.lower().replace("-", "_")
        self.display_name = "Windows Control"
        self.version = version
        self.accent = _ACCENT
        self._color = self._detect_color()

    def _detect_color(self) -> bool:
        if os.environ.get("NO_COLOR"):
            return False
        if not hasattr(sys.stdout, "isatty"):
            return False
        return sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        if not self._color:
            return text
        return f"{code}{text}{_RESET}"

    def print_banner(self):
        inner = 54
        def _box(content: str) -> str:
            pad = inner - _visible_len(content)
            return f"{self._c(_DARK_GRAY, '│')}{content}{' ' * max(0, pad)}{self._c(_DARK_GRAY, '│')}"

        top = self._c(_DARK_GRAY, f"╭{'─' * inner}╮")
        bot = self._c(_DARK_GRAY, f"╰{'─' * inner}╯")

        title = f" {_ICON}  {self._c(_CYAN + _BOLD, 'cli-anything')} {self._c(_DARK_GRAY, '·')} {self._c(self.accent + _BOLD, self.display_name)}"
        ver = f"  {self._c(_DARK_GRAY, f'v{self.version}')}"
        tip = f"  {self._c(_DARK_GRAY, 'Type help for commands, quit to exit')}"

        print(top)
        print(_box(title))
        print(_box(ver))
        print(_box(""))
        print(_box(tip))
        print(bot)
        print()

    def success(self, message: str):
        icon = self._c(_GREEN + _BOLD, "OK")
        print(f"  [{icon}] {self._c(_GREEN, message)}")

    def error(self, message: str):
        icon = self._c(_RED + _BOLD, "FAIL")
        print(f"  [{icon}] {self._c(_RED, message)}", file=sys.stderr)

    def warning(self, message: str):
        icon = self._c(_YELLOW + _BOLD, "WARN")
        print(f"  [{icon}] {self._c(_YELLOW, message)}")

    def info(self, message: str):
        icon = self._c(_BLUE, "INFO")
        print(f"  [{icon}] {self._c(_LIGHT_GRAY, message)}")

    def section(self, title: str):
        print()
        print(f"  {self._c(self.accent + _BOLD, title)}")
        print(f"  {self._c(_DARK_GRAY, '─' * len(title))}")

    def status(self, label: str, value: str):
        lbl = self._c(_GRAY, f"  {label}:")
        val = self._c(_WHITE, f" {value}")
        print(f"{lbl}{val}")

    def help(self, commands: dict):
        self.section("Commands")
        for cmd, desc in commands.items():
            cmd_styled = self._c(self.accent, f"  {cmd:<20}")
            desc_styled = self._c(_GRAY, f" {desc}")
            print(f"{cmd_styled}{desc_styled}")
        print()

    def print_goodbye(self):
        print(f"\n  {_ICON_SMALL} {self._c(_GRAY, 'Goodbye!')}\n")

    def create_prompt_session(self):
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory
            from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
            from prompt_toolkit.styles import Style

            hist_dir = os.path.join(os.path.expanduser("~"), ".cli-anything-windows-control")
            os.makedirs(hist_dir, exist_ok=True)
            hist_file = os.path.join(hist_dir, "history")

            style = Style.from_dict({
                "icon": "#5fd7d7 bold",
                "software": "#ff8700 bold",
                "bracket": "#585858",
                "context": "#bcbcbc",
                "arrow": "#808080",
            })

            return PromptSession(
                history=FileHistory(hist_file),
                auto_suggest=AutoSuggestFromHistory(),
                style=style,
                enable_history_search=True,
            )
        except ImportError:
            return None

    def get_input(self, pt_session, project_name="", modified=False, context="") -> str:
        if pt_session is not None:
            from prompt_toolkit.formatted_text import FormattedText
            tokens = [
                ("class:icon", "◆ "),
                ("class:software", self.software),
                ("class:arrow", " > "),
            ]
            return pt_session.prompt(FormattedText(tokens)).strip()
        else:
            return input(f"{self.software}> ").strip()
