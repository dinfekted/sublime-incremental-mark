import sublime
import sublime_plugin

class Collections():

  def __init__(self):
    self.marks = {}
    self.name = 'incremental-mark-state'

  def get(self, view):
    id = view.id()
    if id not in self.marks:
      self.marks[id] = Collection(view)
    return self.marks[id]

collections = Collections()

class Mark():

  def __init__(self, target, order):
    self.target = target
    self.current = False
    self.order = order

  def clone(self):
    mark = Mark(self.target, self.order)
    mark.current = self.current
    return mark

class Collection():

  def __init__(self, view, name = 'incremental-mark-'):
    self.view = view
    self.marks = {}
    self.mark_icon = 'bookmark'
    self.mark_options = sublime.HIDDEN
    self.maximal_marks_count = 5
    self.name = name
    self.states = []

    for index in range(0, self.maximal_marks_count + 1):
      self.view.erase_regions(name + str(index))

  def get_marks(self):
    state = self.get_state()
    if state not in self.marks:
      self.marks[state] = []

    return self.marks[state]

  def save_state(self):
    old_state = self.get_state(False)

    id = 0
    while id in self.states:
      id += 1

    self.states.append(id)
    if old_state == None:
      self.marks[id] = []
    else:
      marks = []
      for mark in self.marks[old_state]:
        marks.append(mark.clone())

      self.marks[id] = marks

    self.view.add_regions(self._get_state_name(id), [sublime.Region(0, 0)])

    if len(self.states) > 100:
      old_id = self.states.pop(0)
      self.marks.pop(old_id)
      self.view.erase_regions(self._get_state_name(old_id))

    return id

  def get_state(self, create = True):
    for id in reversed(self.states):
      if len(self.view.get_regions(self._get_state_name(id))) > 0:
        return id

    if create:
      return self.save_state()
    else:
      return None

  def add(self, order = None, regions = None):
    target = self._get_next_target()
    order = self._get_next_order(order)

    mark = Mark(target, order)
    self.get_marks().append(mark)

    if regions == None:
      regions = []
      for region in self.view.sel():
        regions.append(region)

    self.view.add_regions(target, regions, "?", self.mark_icon,
      self.mark_options)

    return mark

  def remove(self, mark):
    index = self._get_index(mark)
    if mark == None:
      return

    self.get_marks().pop(index)

    self.view.erase_regions(mark.target)
    self._shift_orders(mark.order, -1)

  def get_next(self, mark, backward = True):
    orders = self._get_orders()
    result, current = None, None
    for index, order in enumerate(orders):
      if backward:
        if order < mark.order and (current == None or current < order):
          current = order
          result = index
      else:
        if order > mark.order and (current == None or current > order):
          current = order
          result = index

    if result == None:
      return None

    return self.get_marks()[result]

  def show(self, mark):
    regions = self.view.get_regions(mark.target)
    if len(regions) == 0:
      return

    self.view.sel().clear()
    self.view.sel().add_all(regions)

  def _get_state_name(self, id):
    return self.name + 'state-' + str(id)

  def _get_next_target(self):
    if len(self.get_marks()) >= self.maximal_marks_count:
      first, index = self.get_first()
      self.get_marks().pop(index)
      self.view.erase_regions(first.target)
      target = first.target
    else:
      for index in range(0, self.maximal_marks_count):
        target = self.name + str(index)
        found = False
        for mark in self.get_marks():
          if mark.target == target:
            found = True

        if not found:
          return target

      raise Exception("Something bad happened: can not allocate target name")

    return target

  def _get_next_order(self, order = None):
    if order == None:
      current, _ = self.get_current()

      if current == None:
        current, _ = self.get_last()

      if current:
        order = current.order + 1
      else:
        order = 0

    self._shift_orders(order)

    return order

  def get_last(self):
    position, mark, order = None, None, None
    for index, current_mark in enumerate(self.get_marks()):
      if order == None or order < current_mark.order:
        order = current_mark.order
        mark = current_mark
        position = index

    return mark, position

  def get_first(self):
    position, mark, order = None, None, None
    for index, current_mark in enumerate(self.get_marks()):
      if order == None or order > current_mark.order:
        order = current_mark.order
        mark = current_mark
        position = index

    return mark, position

  def set_current(self, mark):
    for current_mark in self.get_marks():
      current_mark.current = False

    if mark != None:
      mark.current = True

  def get_current(self):
    for index, mark in enumerate(self.get_marks()):
      if mark.current:
        return mark, index
    return None, None

  def _get_by_order(self, order):
    for index, mark in enumerate(self.get_marks()):
      if mark.order == order:
        return mark, index

    return None, None

  def _get_orders(self):
    orders = []
    for mark in self.get_marks():
      orders.append(mark.order)
    return orders

  def _get_index(self, mark):
    for index, current in enumerate(self.get_marks()):
      if current.order == mark.order:
        return index
    return None, None

  def _shift_orders(self, order, value = 1):
    for mark in self.get_marks():
      if mark.order >= order:
        mark.order += value