import subprocess
import tempfile
from pyi3l.tree import *

def use_layout(ws, layout: Toplevel, workspace_switching: bool = True):
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(layout.to_layout_string().encode("utf-8"))
        tmp.flush()
        subprocess.run([    
            "i3-msg", 
            ";".join([
                f"workspace {ws};" if workspace_switching and (ws is not None) else "",
                "append_layout " + tmp.name
            ])
        ])

def run(d, commands: bool = True, layout: bool = True, workspace_switching: bool = True):
    if layout:
        for ws, layout in d.items():
            use_layout(ws, layout, workspace_switching=workspace_switching)
    if commands:
        cmds = [
            cmd
            for layout in d.values()
            for cmd in layout.to_commands()
        ]
        for cmd in cmds:
            subprocess.run(cmd.to_shell_command() + " &", shell = True)

