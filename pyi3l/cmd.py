from pyi3l.exec import *
from pyi3l.bashify import bashify
import argparse

def apply(d):
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-bash-script", action="store_true")
    parser.add_argument("--skip-commands", action="store_true")
    parser.add_argument("--skip-layout", action="store_true")
    parser.add_argument("--skip-workspace-switching", action="store_true")
    args = parser.parse_args()
    if args.export_bash_script:
        print(bashify(
            d,
            commands=not args.skip_commands,
            layout=not args.skip_layout,
            workspace_switching=not args.skip_workspace_switching,
        ))
    else:
        run(
            d,
            commands=not args.skip_commands,
            layout=not args.skip_layout,
            workspace_switching=not args.skip_workspace_switching,
        )
