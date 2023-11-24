from pyi3l.tree import *

def bashify_layout(ws, layout: Toplevel, workspace_switching: bool = True):
    i3_msg_args = "".join([
        f"workspace {ws}\\;" if workspace_switching and (ws is not None) else "",
        "append_layout $layout_file",
    ])
    return "\n".join([
        "",
        f"## Workspace {ws}",
        "layout_file=$(mktemp)",
        f"echo {shlex.quote(layout.to_layout_string(indent=2))} > $layout_file",
        f'''i3-msg {i3_msg_args}''',
        "rm $layout_file"
    ])


def bashify(d, commands: bool = True, layout: bool = True, workspace_switching: bool = True):
    
    cmds = [
        cmd
        for layout in d.values()
        for cmd in layout.to_commands()
    ]

    return "#!/usr/bin/bash\n\n" + "\n".join([
        *([
            "# Set up workspaces",
            *map(lambda x: bashify_layout(x[0], x[1], workspace_switching=workspace_switching), d.items()),
        ] if layout else []),
        "",
        "",
        *([
            "# Start the applications",
            *map(lambda cmd: cmd.to_shell_command() + "&", cmds),
        ] if commands else []),
    ])
