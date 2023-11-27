from typing import Optional
from functools import partial
from .tree import WindowContent, SystemCommand, Command, Swallow
from .patterns import Literal, Anything, AnyOf

def firefox():
    return WindowContent(
        swallows = [Swallow(
            win_class = Literal("firefox"),
            instance = Literal("Navigator"),
        )],
        default_name = "Firefox",
        flatpak_ids = ["org.mozilla.Firefox"],
        commands = [
            SystemCommand(["firefox"]),
        ],
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
