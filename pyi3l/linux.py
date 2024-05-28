from dataclasses import dataclass, replace
from typing import Optional
from functools import partial
from .tree import WindowContent, SystemCommand, Command, Swallow, CmdModifier
from .patterns import Literal, Anything, AnyOf

@dataclass
class WorkingDir(CmdModifier):
    directory: str

    def adjust_command(self, cmd: Command):
        return SystemCommand([
            "env",
            "-C",
            self.directory,
            "--",
            *cmd.to_system_command(),
        ])

def firefox():
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("firefox") | Literal("org.mozilla.firefox"),
            instance = Literal("Navigator"),
        )],
        default_name = "Firefox",
        flatpak_ids = ["org.mozilla.Firefox"],
        commands = [
            SystemCommand(["firefox"]),
        ],
    )

def chromium(url=None):
    return WindowContent(
        swallows = [
            Swallow(
                win_class=Literal("Chromium-browser"),
                instance=Literal("chromium-browser"),
            ),
        ],
        commands = [SystemCommand(["chromium", *([] if url is None else [url])])],
        default_name = "Chromium" if url is None else f"Chromium: {url}"
    )

def chromium_app(url, instance_override = None):
    if instance_override is None:
        import re
        from urllib.parse import urlsplit
        spl = urlsplit(url)

        instance = re.sub(
            r'[^a-zA-Z0-9_.-]',
            '_',
            spl.netloc + (f'_{spl.path}' if spl.path != '' else '')
        )
    else:
        instance = instance_override or url

    return WindowContent(
        swallows = [
            Swallow(
                win_class=Literal("Chromium-browser"),
                instance=Literal(instance),
            ),
        ],
        commands = [SystemCommand(["chromium", f"--app={url}"])],
        default_name = url
    )

def geany():
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("Geany"),
            instance = Literal("geany"),
        )],
        default_name = "Geany",
        flatpak_ids = ["org.geany.Geany"],
        commands = [
            SystemCommand(["geany"]),
        ],
    )

def jetbrains_ide(ide_id, ide_name, project_name):
    tpe = Literal(f"jetbrains-{ide_id}") + AnyOf([Literal("-ce"), Literal("")])
    return WindowContent(
        swallows = [Swallow(
            win_class = tpe,
            instance = tpe,
            title = Literal(project_name + " – ") + Anything() if project_name is not None else None,
        )],
        default_name = ide_name,
        commands = [
            SystemCommand([ide_id + ".sh"]),
        ]
    )

idea = partial(jetbrains_ide, "idea", "IntelliJ IDEA")
pycharm = partial(jetbrains_ide, "pycharm", "PyCharm")

def thunderbird():
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("thunderbird"),
            instance = Literal("Mail"),
        )],
        commands = [SystemCommand(["thunderbird"])],
        flatpak_ids = ["org.mozilla.Thunderbird"],
        default_name = "Thunderbird",
    )

def signal():
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("Signal"),
            instance = Literal("signal"),
        )],
        commands = [SystemCommand(["signal-desktop"])],
        flatpak_ids = ["org.signal.Signal"],
        default_name = "Signal",
    )

def element_io():
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("Element"),
            instance = Literal("element"),
        )],
        commands = [SystemCommand(["element-desktop"])],
        flatpak_ids = ["im.riot.Riot"],
        default_name = "Element",
    )


def toggl():
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("Toggl Desktop"),
            instance = Literal("TogglDesktop"),
        )],
        commands = [SystemCommand(["TogglDesktop.sh"])],
        flatpak_ids = ["com.toggl.TogglDesktop"],
        default_name = "Toggl",
    )


def toggl_chromium():
    return replace(
        chromium_app("chrome-extension://oejgccbfbmkkpaidnkphaiaecficdnfn/src/pages/popup/index.html"),
        default_name = "Toggl gadget",
    )


def xfce4_terminal(title = None, command: Optional[Command] = None):
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("Xfce4-terminal"),
            instance = Literal("xfce4-terminal"),
            title = Literal("Terminal - ") + Anything() if title is None else Literal(title),
        )],
        default_name = title or "Terminal",
        commands = [
            SystemCommand([
                "xfce4-terminal",
                *([f"--title={title}"] if title is not None else []),
                *(["-x", *command.to_system_command()] if command is not None else []),
            ]),
        ]
    )




def discord():
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("discord"),
            instance = Literal("discord"),
            title = Literal("Friends - Discord"),
        )],
        default_name = "Discord",
        commands = [SystemCommand(["discord"])],
        flatpak_ids = ["com.discordapp.Discord"],
    )
