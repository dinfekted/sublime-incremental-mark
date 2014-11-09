import sublime
import sublime_plugin

from IncrementalMark import incremental_mark

last_selection = None
allowed_commands = None

def _is_command_allowed(command, args):
  global allowed_commands

  if allowed_commands == None:
    settings = sublime.load_settings('IncremenetalMark.sublime-settings')
    allowed_commands = settings.get('commands', [])

  return [command, args] in allowed_commands or command in allowed_commands

class Listener(sublime_plugin.EventListener):
  def on_selection_modified_async(self, view):
    global previous_selection, last_selection

    previous_selection = last_selection

    last_selection = []
    for sel in view.sel():
      last_selection.append(sel)

  def on_text_command(self, view, command_name, args):
    self._add_mark(view, command_name, args)

  def on_window_command(self, window, command_name, args):
    self._add_mark(window.active_view(), command_name, args)

  def _add_mark(self, view, command, args):
    global last_selection

    if last_selection == None or not _is_command_allowed(command, args):
      return

    marks = incremental_mark.collections.get(view)

    marks.save_state()
    marks.set_current(marks.add(None, last_selection))