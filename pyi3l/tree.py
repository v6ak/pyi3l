from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from .util import only_nonnone, remove_keys, noneize_defaults
from .patterns import Pattern
import json
from typing import List, Optional, Union
import subprocess
import shlex
from functools import partial

class Command(ABC):
    @abstractmethod
    def run(self):
        pass
    @abstractmethod
    def to_shell_command(self):
        pass
    @abstractmethod
    def to_system_command(self):
        pass

@dataclass
class ShellCommand(Command):
    command: str

    def run(self):
        subprocess.run(self.to_shell_command())

    def to_shell_command(self):
        return self.command

    def to_system_command(self):
        return ["bash", "-c", self.command]

@dataclass
class SystemCommand(Command):
    command: List[str]

    def run(self):
        subprocess.run(self.command)

    def to_shell_command(self):
        return " ".join(map(shlex.quote, self.command))

    def to_system_command(self):
        return self.command

@dataclass
class PartialSystemCommand:
    command: List[str]

    def __call__(self, *args):
        return SystemCommand([*self.command, *args])


class Element(ABC):
    @abstractmethod
    def to_layout(self):
        pass

    @abstractmethod
    def to_commands(self):
        pass

    @abstractmethod
    def without_marks(self): pass

    @abstractmethod
    def map_windows(self, f): pass

class Toplevel(Element):
    @abstractmethod
    def to_layout_string(self, indent = None):
        pass

    @staticmethod
    def import_toplevel(j):
        if isinstance(j, list):
            if len(j) == 1:
                return Node.import_node(j[0])
            else:
                return Multi.import_multi(j)
        else:
            return Node.import_node(j)

class Node(Toplevel):
    def to_layout_string(self, indent = None):
        return json.dumps(self.to_layout(), indent=indent)

    @staticmethod
    def import_node(j):
        if j.get("layout") is None:
            return Window.import_window(j)
        else:
            return Layout.import_layout(j)

@dataclass
class RawElement(Node):
    raw: dict
    commands: Optional[List[Command]]

    def to_layout(self):
        return raw

    def to_commands(self):
        return self.commands or []

    def map_windows(self, f):
        return self

    def without_marks(self):
        return self

@dataclass
class Multi(Toplevel):
    elements: List[Element]

    def to_layout(self):
        return list(map(lambda e: e.to_layout(), self.elements))

    def to_commands(self):
        return [
            cmd
            for e in self.elements
            for cmd in e.to_commands()
        ]

    def to_layout_string(self, indent = None):
        l = self.to_layout()
        return "\n\n".join(map(lambda e: json.dumps(e, indent=indent), l))

    def map_windows(self, f):
        return Multi(elements=list(map(lambda el: el.map_windows(f), self.elements)))

    def without_marks(self):
        return Multi(elements=list(map(lambda el: el.without_marks(), self.elements)))

    @staticmethod
    def import_multi(l):
        return Multi(list(map(Node.import_node, l)))

@dataclass
class Swallow:
    win_class: Optional[Pattern] = None
    instance: Optional[Pattern] = None
    machine: Optional[Pattern] = None
    title: Optional[Pattern] = None
    window_role: Optional[Pattern] = None

    def to_json(self):
        def re(value: Optional[Pattern]):
            if value is None:
                return None
            else:
                return f"^{value.to_pcre()}$"

        return only_nonnone({
            "class": re(self.win_class),
            "instance": re(self.instance),
            "machine": re(self.machine),
            "title": re(self.title),
            "window_role": re(self.window_role),
        })

    @staticmethod
    def import_swallow(j):
        return Swallow(
            win_class = Pattern.import_pattern(j.get("class")),
            instance = Pattern.import_pattern(j.get("instance")),
            machine = Pattern.import_pattern(j.get("machine")),
            title = Pattern.import_pattern(j.get("title")),
            window_role = Pattern.import_pattern(j.get("window_role")),
        )

@dataclass
class Geometry:
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

    others: Optional[dict] = None

    def to_layout():
        return {
            **only_nonnone({
                "x": self.x,
                "y": self.y,
                "width": self.width,
                "height": self.height,
            }),
            **(self.others or {}),
        }

    @staticmethod
    def import_geometry(j):
        if j is None:
            return None
        else:
            KEYWORDS = {"x", "y", "width", "height"}
            return Geometry(
                x = j.get("x"),
                y = j.get("y"),
                height = j.get("height"),
                width = j.get("width"),
                others = noneize_defaults(remove_keys(j, KEYWORDS), {}),
            )

@dataclass
class WindowContent:
    swallows: List[Swallow]
    default_name: Optional[str] = None
    commands: Optional[List[Command]] = None
    flatpak_ids: Optional[List[str]] = None

    def as_flatpak(self):
        return replace(
            self,
            commands=list(map(lambda id: SystemCommand(["flatpak", "run", id]), self.flatpak_ids)),
        )

    def placeholder_only(self):
        return replace(
            self,
            commands=[],
            flatpak_ids=[],
        )

    @staticmethod
    def import_content(j):
        return WindowContent(
            swallows = list(map(Swallow.import_swallow, j.get("swallows"))),
        )

@dataclass
class Window(Node):
    content: WindowContent
    name: Optional[str] = None
    percent: Optional[float] = None
    marks: Optional[List[str]] = None
    border: Optional[str] = None
    current_border_width: Optional[int] = None
    floating: Optional[str] = None
    type: Optional[str] = None
    geometry: Optional[Geometry] = None

    others: Optional[dict] = None

    def to_commands(self):
        return self.content.commands or []

    def to_layout(self):
        return {
            **only_nonnone({
                "name": self.name or self.content.default_name,
                "percent": self.percent,
                "marks": self.marks,
                "swallows": list(map(lambda sw: sw.to_json(), self.content.swallows)),
                "border": self.border,
                "current_border_width": self.current_border_width,
                "floating": self.floating,
                "type": self.type,
                "geometry": None if self.geometry is None else self.geometry.to_layout(),
            }),
            **(self.others or {}),
        }

    @staticmethod
    def import_window(j):
        KEYWORDS = {
            "name", "percent", "marks", "swallows", "border", "current_border_width", "floating", "type", "geometry"
        }
        return Window(
            content = WindowContent.import_content(j),
            name = j.get("name"),
            percent = j.get("percent"),
            marks = noneize_defaults(j.get("marks"), []),
            border = noneize_defaults(j.get("border"), "normal"),
            current_border_width = noneize_defaults(j.get("current_border_width"), 2),
            floating = noneize_defaults(j.get("floating"), "auto_off"),
            type = noneize_defaults(j.get("type"), "con"),
            geometry = noneize_defaults(Geometry.import_geometry(j.get("geometry")), Geometry()),
            others = noneize_defaults(remove_keys(j, KEYWORDS), {}),
        )

    def map_windows(self, f):
        return f(self)

    def map_content(self, f):
        return replace(
            self,
            content=f(self.content)
        )

    def without_marks(self):
        return replace(
            self,
            marks=None
        )

    def without_percent(self):
        return replace(
            self,
            percent=None
        )

@dataclass
class Layout(Node):
    layout: str
    nodes: List[Element]
    marks: Optional[List[str]] = None
    percent: Optional[float] = None
    border: Optional[str] = None
    floating: Optional[str] = None
    type: Optional[str] = None
    rect: Optional[Geometry] = None

    others: Optional[dict] = None

    def to_layout(self):
        return {
            **only_nonnone({
                "layout": self.layout,
                "nodes": list(map(lambda e: e.to_layout(), self.nodes)),
                "marks": self.marks,
                "percent": self.percent,
                "border": self.border,
                "floating": self.floating,
                "type": self.type,
                "rect": None if self.rect is None else self.rect.to_layout(),

            }),
            **(self.others or {}),
        }

    @staticmethod
    def import_layout(j):
        KEYWORDS={"nodes", "marks", "percent", "layout", "border", "floating", "type", "rect"}
        return Layout(
            marks=noneize_defaults(j.get("marks"), []),
            percent=j.get("percent"),
            layout=j.get("layout"),
            nodes=list(map(Node.import_node, j["nodes"])),
            border = noneize_defaults(j.get("border"), "normal"),
            floating = noneize_defaults(j.get("floating"), "auto_off"),
            type = noneize_defaults(j.get("type"), "con"),
            rect = noneize_defaults(Geometry.import_geometry(j.get("rect")), Geometry()),
            others = noneize_defaults(remove_keys(j, KEYWORDS), {})
        )

    def to_commands(self):
        return [
            cmd
            for e in self.nodes
            for cmd in e.to_commands()
        ]

    def map_windows(self, f):
        return self.map_nodes(lambda el: el.map_windows(f))

    def without_marks(self):
        return self.map_nodes(lambda el: el.without_marks(f))

    def map_nodes(self, f):
        return replace(
            self,
            nodes=list(map(f, self.nodes)),
        )

FloatingLayout = partial(Layout, type="floating_con")

Horizontal = partial(Layout, "splith")
Vertical = partial(Layout, "splitv")
Tabbed = partial(Layout, "tabbed")
Stacked = partial(Layout, "stacked")

FloatingHorizontal = partial(FloatingLayout, "splith")
FloatingVertical = partial(FloatingLayout, "splitv")
FloatingTabbed = partial(FloatingLayout, "tabbed")
FloatingStacked = partial(FloatingLayout, "stacked")


class CmdModifier(ABC):

    def __call__(self, arg: Union[WindowContent, Command, Window]):
        if isinstance(arg, WindowContent):
            return self.adjust_content(arg)
        elif isinstance(arg, Window):
            return self.adjust_window(arg)
        elif isinstance(arg, Command):
            return self.adjust_command(arg)
        raise ValueError(f"Unexpected arg type: {arg}")

    def adjust_window(self, win: Window):
        return win.map_content(self.adjust_content)

    @abstractmethod
    def adjust_command(self, command: Command): pass

    def adjust_content(self, content: WindowContent):
        return WindowContent(
            swallows = content.swallows,
            default_name = content.default_name,
            commands = list(map(
                self.adjust_command,
                content.commands or []
            )),
            flatpak_ids = content.flatpak_ids,
        )
