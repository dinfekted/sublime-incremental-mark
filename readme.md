# Sublime IncremenentalMark plugin

Insert mark automatically on executing commands specified in settings.


### Installation

This plugin is part of [sublime-enhanced](http://github.com/Shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/Shagabutdinov/sublime-enhanced)
package.


### Usage

Hit any commmand specified in IncrementalMark.sublime-settings, it'll add mark
mark automatically so you can come back to previous location. There is keyboard
shortcut for removing current marks setted. Does not set more that 5 marks.
Reset mark when navigating by mark set. Could work badly with "undo" as "undo"
removes marks from view.


### Settings

Settings stored in IncrementalMark.sublime-settings.


##### "commands"

Array of commands that adds mark after execution; each command should be in
following format [command_name, command_args] or command_name where command_name
is name of command that is executed (e.g. "move") and command_args is hash table
of args for this command.

Example:

  ```
  "commands": [
    ["move_to", {"extend": false, "to": "bof"}]
  ]
  ```

### Commands

| Description        | Keyboard shortcut | Command palette                |
|--------------------|-------------------|--------------------------------|
| Goto mark forward  | alt+r             | IncrementalMark: Goto next     |
| Goto mark backward | alt+shift+r       | IncrementalMark: Goto previous |
| Clean marks        | alt+ctrl+r        | IncrementalMark: Clean         |