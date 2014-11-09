import sublime
import sublime_plugin

from IncrementalMark import incremental_mark

class GotoIncrementalMark(sublime_plugin.TextCommand):
  def __init__(self, view):
    super().__init__(view)
    self.last_backward = None

  def run(self, edit, backward = True, unset = True, set = True):
    marks = incremental_mark.collections.get(self.view)
    marks.save_state()

    if backward:
      regions = self._go_backward(marks, unset, set)
    else:
      regions = self._go_forward(marks, unset, set)

    self.last_backward = backward

    if regions == None:
      return

    if len(regions) > 0:
      self.view.sel().clear()
      self.view.sel().add_all(regions)
      self.view.show(regions[0])

  def _go_backward(self, marks, unset, set):
    current, _ = marks.get_current()

    if self.last_backward == False:
      if current != None:
        current = marks.get_next(current, True)

    if current == None:
      current, _ = marks.get_last()
      if current == None:
        return

    regions = self.view.get_regions(current.target)

    next_mark = marks.get_next(current, True)
    while next_mark != None and regions == list(self.view.sel()):
      regions = self.view.get_regions(next_mark.target)
      next_mark = marks.get_next(next_mark, True)

    if unset and set:
      self.view.erase_regions(current.target)
      self.view.add_regions(current.target, self.view.sel(), "?", 'bookmark', sublime.HIDDEN)
    elif unset:
      marks.remove(current)

    marks.set_current(next_mark)

    return regions

  def _go_forward(self, marks, unset, set):
    current, _ = marks.get_current()

    if self.last_backward == True:
      if current != None:
        current = marks.get_next(current, False)

    if current == None:
      current, _ = marks.get_first()
      if current == None:
        return

    regions = self.view.get_regions(current.target)

    next_mark = marks.get_next(current, False)
    while next_mark != None and regions == list(self.view.sel()):
      regions = self.view.get_regions(next_mark.target)
      next_mark = marks.get_next(next_mark, False)

    if unset and set:
      self.view.erase_regions(current.target)
      self.view.add_regions(current.target, self.view.sel(), "?", 'bookmark', sublime.HIDDEN)
    elif unset:
      marks.remove(current)

    marks.set_current(next_mark)

    return regions

class InsertIncrementalMark(sublime_plugin.TextCommand):
  def run(self, edit):
    marks = incremental_mark.collections.get(self.view)

    marks.save_state()
    mark = marks.add()
    marks.set_current(mark)

class InsertIncrementalMarkByCmd(sublime_plugin.TextCommand):
  def __init__(self, view):
    super().__init__(view)
    self.last_command = None

  def run(self, edit, command):
    if self.last_command == command:
      return

    self.last_command = command
    self.view.run_command('insert_incremental_mark')

class CleanIncrementalMarks(sublime_plugin.TextCommand):
  def run(self, edit):
    marks = incremental_mark.collections.get(self.view)

    while len(marks.get_marks()) > 0:
      marks.remove(marks.get_marks()[0])