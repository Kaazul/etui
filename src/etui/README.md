# ETUI

This TUI is intened for launching python CLI scripts from one central point. To control it
either the mouse or the UP, DOWN and ENTER keys on the keyboard can be used. The Header
displays the name of the current menu, the version of ETUI and the current time. The
footer displays additional key bindings. There are two keys that work everywhere in this
TUI: The ESC key to go back to the former menu and the Q Key to quit the application. The
same can be achieved when the Key-Binding in the footer is clicked on.

## ScriptLauncher

The ScriptLauncher consists of the following parts:

### Script List

By clicking a script folder in the folder dropdown all scripts in this folder will be
listed in the script list. If you click on the script the possible arguments to start the
script with will be displayed in the Argument Panel. One folder that is included by
default is the tests folder of the ETUI codebase.

### Argument Panel

When a script is chosen, the possible arguments will be displayed. If there are
(sub)commands for the script, a dropdown list of all commands will be displayed on top of
the Argument panel. Arguments can either be written in or checked with a checkbox.

### Script Buttons

There are three script buttons. The first starts the script and the last stops it by
sending a SIGTERM signal to the process which runs the script. The second button clears
the output box.

### Output Box
The output box displays a live view of what the script puts out to STDOUT and to STDERR.
So, the output and the errors will be displayed. Everything that is shown here will
additionally be logged on each run.

### Input Box
The Input Box can be used to send messages to the script. The Input Box is only accesible
when a script is running.

## LogViewer

The LogViewer displays all the currently stored logs of previous runs of python scripts
started with this TUI. The logs will automatically be deleted after 30 days have passed.
The log folder is in the root path of the codebase of ETUI. Each logfile contains the name,
the date and the time when it was started.

## ScriptFolder Manager

The ScriptFolder Manager is used for adding or removing script folders. When the option
to restore default is used every added script folder will be lost in the folder list! To
add a script folder you only have to give it a unique name (this is the name that will be
displayed in the folder list in the ScriptLauncher) and the path to the folder either
absolute or relative to the root path of the ETUI codebase. A python executable is
optional, if none is given the python version of the ETUI codebase will be used.
Furthermore, you can decide if the scripts should be run from the folder path (default)
or from the root path of the ETUI codebase.
