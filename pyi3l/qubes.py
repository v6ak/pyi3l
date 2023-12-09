from dataclasses import dataclass
from typing import Union, Optional

from pyi3l.tree import Command, WindowContent, SystemCommand, Window, Swallow, CmdModifier
from pyi3l.patterns import Pattern, Literal, Anything

@dataclass
class Qube(CmdModifier):
    name: str
    unicode_titles: bool = False

    def adjust_content(self, content: WindowContent):
        return WindowContent(
            swallows = list(map(self.adjust_swallow, content.swallows)),
            default_name = f"{self.name} » {content.default_name or '???'}",
            commands = list(map(
                self.adjust_command,
                content.commands or []
            )),
            flatpak_ids = None,
        )

    def _prepend_name(self, pattern: Pattern, swallow: Swallow):
        prefix = Literal(self.name + ":")
        if pattern is None:
            if (swallow.win_class is not None) or (swallow.instance is not None):
                # qube will be filtered by another attribute
                return None
            else:
                return prefix + Anything()
        else:
            return prefix + pattern

    def adjust_swallow(self, swallow: Swallow):
        return Swallow(
            win_class = self._prepend_name(swallow.win_class, swallow),
            instance = self._prepend_name(swallow.instance, swallow),
            machine = swallow.machine,
            title = self._adjust_title(swallow.title),
            window_role = swallow.window_role,
        )
        
    def adjust_command(self, command: Command):
        return SystemCommand([
            "qvm-run",
            self.name,
            "--",
            command.to_shell_command()
        ])

    def _adjust_title(self, title: Optional[Pattern]):
        if title is None:
            return None
        elif self.unicode_titles:
            return title
        else:
            return title.map_chars(self._sanitize_title)

    def _sanitize_title(self, s: str):
        return "".join(
            map(
                lambda x: chr(x) if x<128 else '_',
                s.encode("utf-8")
            )
        )
