# ETUI
CLI Scriptlauncher in a simple python TUI

## Install

First, find a nice spot in your directory to git clone the repo by using

        git clone https://github.com/Kaazul/etui.git

Then you can move to the root directory of this git repo and run the install.sh file
with bash.

        bash install.sh

This will automatically install all necessary tools and setup this project. It installs
the python package management tool **uv**, the tool **pre-commit** for automatic
format and linter checks when commiting a change (only needed if you want to contribute)
and adds the command **etui** to the shell (by adding a function named etui to .bashrc
of the user), if it is not already in use.

After installing, you can start the TUI by using the command

        etui
or by using **uv** to run the corresponding startup script **main.py**

        uv run /path/to/etui/src/main.py

The main screen of the TUI currently leads to 3 different sub-screens: ScriptLauncher,
LogViewer and Help. In the help screen you will find further info how to use the TUI.
With the LogViewer the logs of the script that have been run with the ScriptLauncher can
be read. In the ScriptLauncher the CLI scripts in specific folders can be chosen to run.
The output of the script is displayed in the TUI and also logged to a run-specific
logfile. It is furthermore possible to take user input, if the script waits for it. The
script can also be terminated safely at any time with a button. The TUI can be
controlled with the mouse and the UP and DOWN Keys.

## Use case

I once had the not so small task to update/rewrite a lot of python scripts. These
scripts where used in-house and started by users as command line scripts. The scripts
themselves where in a few different folders and started with a few different python
versions. To ease the change process for the users I created a TUI as a starting point
for all of these scripts. This also reduced user error, because they didn't have to
remember which python version to use, or exactly which arguments or flags to set,
because these were also displayed in the TUI. In the background I could create the new
scripts and then switch them out safely.

So, if you have exactly this very specific and niche use case, then this ETUI is for you.
Besides that, it can also be useful if you don't have a graphical user interface and
like the aesthetics of a TUI and the comfortability to run your python scripts from one
central point.

## Future Goals

 - Implement a settings screen (for setting script folders, log retention settings, ...)
 - Implement for more than just python scripts

I already had a user login page implemented, but because it was work-specific it didn't
make the cut in the fork. In the future, i plan to have some modular option to include a
user login.

## Contributing

Thanks for your interest in contributing! 🎉
Contributions of all kinds are welcome: bug reports, feature requests, documentation
improvements, and code.

This project is maintained in my free time, so please be patient in discussions and
reviews.

### Ways to Contribute

You can contribute by:
- Reporting bugs
- Suggesting features or improvements
- Improving documentation
- Submitting code changes (bug fixes, refactors, new features)

If you’re unsure where to start, feel free to open an issue and ask.

### Development Setup

Follow the install steps, but run the install script with --dev flag to also make sure
pre-commit is properly setup:

    bash install.sh --dev
