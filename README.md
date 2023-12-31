# Python-based DSL for i3 layouts

…and maybe also for Sway, if you slightly adjust it.

## Features

### Define layout and commands at single place

With i3 layouts, you need to define layout separately from commands you run. For example, you add
this to your layout:

    {
      "name": "Firefox",
      "swallows": [
        {
          "class": "^firefox$",
          "instance": "^Navigator$"
        }
      ]
    },

Then, you add this to some enclosing script:

    firefox&

With this DSL, you can write both on single place. Without using any other features (see below), it
could look like this:

    Window(WindowContent(
        swallows = [Swallow(
            win_class = Literal("firefox"),
            instance = Literal("Navigator"),
        )],
        default_name = "Firefox",
        commands = [SystemCommand(["firefox"])],
    ))

### No clutter in exported layouts

When you export a layout by i3-save-layout, you get many lines of clutter, and it takes some time to find the important parts:

    {
        "border": "normal",
        "current_border_width": 2,
        "floating": "auto_off",
        "geometry": {
           "height": 1050,
           "width": 1290,
           "x": 0,
           "y": 0
        },
        "marks": [],
        "name": "Welcome to Firefox ___ Mozilla Firefox",
        "percent": 0.05,
        "swallows": [
           {
           // "class": "^disp4202\\:firefox$",
           // "instance": "^disp4202\\:Navigator$",
           // "title": "^Welcome\\ to\\ Firefox\\ ___\\ Mozilla\\ Firefox$"
           }
        ],
        "type": "con"
    },

While pyi3l-save-tree layout isn't perfect and there is some room for improvement, its output is shorter much more readable:

    Window(
        WindowContent(
            [
                Swallow(
                    win_class=Literal("disp4202:firefox"),
                    instance=Literal("disp4202:Navigator"),
                    title=Literal("Welcome to Firefox ___ Mozilla Firefox"),
                )
            ]
        ),
        name="Welcome to Firefox ___ Mozilla Firefox",
        percent=0.05,
        others={
            "geometry": {"height": 1050, "width": 1290, "x": 0, "y": 0}
        },
    ),

There are some ideas how to make it even more concise and better maintainable.

### Reusable parts

Do you feel like your layouts are copy&paste? Or maybe you have multiple very similar layouts.

JSON-based layouts have no solution for that. Python has.

### Predefined parts

There are few predefined items for some common applications, see linux.py.

In the example with Firefox above, you can use just this instead:

    Window(firefox())

Note that there might be some differences between Linux distros or app variants
(Firefox vs. Firefox ESR), so some predefined parts might need few adjustments.

### Don't repeat yourself!

The example with Firefox is rather simple. Imagine having a predefined terminal window like this:

    xfce4-terminal \
        '--title=Docspell UI build' \
        -x env -C /home/user/docspell project/dev-ui-build.sh watch-js watch-css

With traditional layouts, you need to repeat the title later:

    {
      "name": "Docspell UI build",
      "percent": 0.319672131147541,
      "swallows": [
        {
          "class": "^Xfce4-terminal$",
          "instance": "^xfce4-terminal$",
          "title": "^Docspell UI build$"
        }
      ]
    }

Every time you want to change the title, you need to change it on both places. Or maybe on three,
if you want to also change the placeholder name. With this DSL, you write the name just once, which
simplifies the maintenance:

    Window(
        xfce4_terminal(
            title="Docspell UI build",
            command=SystemCommand("env", "-C", "/home/user/docspell", 'project/dev-ui-build.sh', 'watch-js', 'watch-css'),
        ),
        percent=0.319672131147541,
    )

### Reusable command prefixes

Sometimes, you might have multiple commands that run in the same directory or with the same
environment variables. This is easy to do with PartialSystemCommand:

    ds_dir = PartialSystemCommand(["env", "-C", "/home/user/docspell"])
    …
    Vertical([
        Window(
            xfce4_terminal(
                title="Docspell SBT",
                command=ds_dir('DOCSPELL_ENV=dev', 'SBT_OPTS=-Xmx3G', 'sbt'),
            ),
            percent=0.680327868852459,
        ),
        Window(
            xfce4_terminal(
                title="Docspell UI build",
                command=ds_dir('project/dev-ui-build.sh', 'watch-js', 'watch-css'),
            ),
            percent=0.319672131147541,
        ),
    ], marks=["docspell-compilation"]),

### No hassle with nested quotes

Have you ever had issues with nested quotes in commands like this?

    qvm-run docspell -- 'xfce4-terminal '"'"'--title=Docspell SBT'"'"' -x env -C /home/user/docspell DOCSPELL_ENV=dev SBT_OPTS=-Xmx3G sbt'

Maybe they can be adjusted to be somewhat better, but still… With pyi3l, you can get rid of them:

    ds_dir = PartialSystemCommand(["env", "-C", "/home/user/docspell"])
    …
    Qube("docspell")(
        xfce4_terminal(
            title="Docspell SBT",
            command=ds_dir('DOCSPELL_ENV=dev', 'SBT_OPTS=-Xmx3G', 'sbt'),
        )
    )

### No annoying forgotten commas

In JSON layouts, it is easy to forget a comma or add an extra one. Especially when JSON doesn't
allow adding one extra trailing comma. What's worse, you get an error without a line number:

    ERROR: Could not parse "/tmp/tmp.LdxNmsl771" as JSON.
    [{"success":false,"error":"Could not parse \"/tmp/tmp.LdxNmsl771\" as JSON."}]

This cannot happen with pyi3l:

1. Python allows extra trailing comma, so it is harder to do it wrong.
2. When you do it wrong, Python will tell you the line number.

### Qubes OS support

Qubes OS allows you to isolate some application in separate virtual machines (called qubes), while
maintaining a seamless UI. Each window is marked, so you know what qube it belongs to.

You need to make some adjustments for how you can wrap the window content to `Qube("…")(…)`
like this:

    Window(Qube("toggl")(toggl())),

This adjusts layout rules (window class, window instance, placeholder title) and the command
(`qvm-run qube-name original-command`) at the same time.

But maybe you want to specify qube name just once for all the windows in the layout. This is also
possible:

    #!/usr/bin/python
    from pyi3l import *
    from pyi3l.cmd import apply

    ds_dir = PartialSystemCommand(["env", "-C", "/home/user/docspell"])

    apply({
        3: Horizontal([
            Tabbed([
                Window(firefox()),
                Vertical([
                    Window(
                        xfce4_terminal(
                            title="Docspell SBT",
                            command=ds_dir('DOCSPELL_ENV=dev', 'SBT_OPTS=-Xmx3G', 'sbt'),
                        ),
                        percent=0.680327868852459,
                    ),
                    Window(
                        xfce4_terminal(
                            title="Docspell UI build",
                            command=ds_dir('project/dev-ui-build.sh', 'watch-js', 'watch-css'),
                        ),
                        percent=0.319672131147541,
                    ),
                ], marks=["docspell-compilation"]),
            ]),
            Tabbed([
                Window(idea("docspell-root")),
                Window(xfce4_terminal()),
            ]),
        ]).map_windows(Qube("docspell")),
        # The .map_windows(Qube("docspell")) ensures everything runs in `docspell` qube
    })

### Much smaller and more readable code

Look at the example for Qubes OS above. The code is much denser than the resulting Bash equivalent.
You can save it to docspell.py and run `./docspell.py --export` to get equivalent Bash code:


    #!/usr/bin/bash

    # Set up workspaces

    ## Workspace 3
    layout_file=$(mktemp)
    echo '{
      "layout": "splith",
      "nodes": [
        {
          "layout": "tabbed",
          "nodes": [
            {
              "name": "docspell \u00bb Firefox",
              "swallows": [
                {
                  "class": "^docspell:firefox$",
                  "instance": "^docspell:Navigator$"
                }
              ]
            },
            {
              "layout": "splitv",
              "nodes": [
                {
                  "name": "docspell \u00bb Docspell SBT",
                  "percent": 0.680327868852459,
                  "swallows": [
                    {
                      "class": "^docspell:Xfce4-terminal$",
                      "instance": "^docspell:xfce4-terminal$",
                      "title": "^Docspell SBT$"
                    }
                  ]
                },
                {
                  "name": "docspell \u00bb Docspell UI build",
                  "percent": 0.319672131147541,
                  "swallows": [
                    {
                      "class": "^docspell:Xfce4-terminal$",
                      "instance": "^docspell:xfce4-terminal$",
                      "title": "^Docspell UI build$"
                    }
                  ]
                }
              ],
              "marks": [
                "docspell-compilation"
              ]
            }
          ]
        },
        {
          "layout": "tabbed",
          "nodes": [
            {
              "name": "docspell \u00bb IntelliJ IDEA",
              "swallows": [
                {
                  "class": "^docspell:jetbrains-idea(-ce|)$",
                  "instance": "^docspell:jetbrains-idea(-ce|)$",
                  "title": "^docspell-root ___ .*$"
                }
              ]
            },
            {
              "name": "docspell \u00bb Terminal",
              "swallows": [
                {
                  "class": "^docspell:Xfce4-terminal$",
                  "instance": "^docspell:xfce4-terminal$",
                  "title": "^Terminal - .*$"
                }
              ]
            }
          ]
        }
      ]
    }' > $layout_file
    i3-msg workspace 3\;append_layout $layout_file
    rm $layout_file


    # Start the applications
    qvm-run docspell -- firefox&
    qvm-run docspell -- 'xfce4-terminal '"'"'--title=Docspell SBT'"'"' -x env -C /home/user/docspell DOCSPELL_ENV=dev SBT_OPTS=-Xmx3G sbt'&
    qvm-run docspell -- 'xfce4-terminal '"'"'--title=Docspell UI build'"'"' -x env -C /home/user/docspell project/dev-ui-build.sh watch-js watch-css'&
    qvm-run docspell -- idea.sh&
    qvm-run docspell -- xfce4-terminal&

Maybe the Bash code could be someshat improved. On the other hand, the resulting code is much
simpler than the output of i3-save-tree, and still much more complex than the DSL.

## Limitations

* Qubes OS titles aren't compatible with raw patterns
* We expect no special characters to occur in temporary file names.

## Ideas for future development

* Import existing JSON layouts. WIP in import.py. (It might look like the same job as importing layouts from i3-save-layout, but there are some differences, as [described in issue #7](https://github.com/v6ak/pyi3l/issues/7).)
* Run-or-focus semantic
