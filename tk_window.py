#!/usr/bin/env python

#
# tk_window.py
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: GPLv2
#


from Tkinter import Tk, TclError
from ttk import Frame

class tk_window(object):
	_ret = None
	_frame = None
	_master = None
	_child = None
	_destroyed = False
	_parent = None

	def __init__(self, classname, classtitle):
		self._master = Tk(className=classname)
		self._master.protocol('WM_DELETE_WINDOW', self.destroy)
		super(tk_window, self).__init__()

		self._parent = None
		self._child = None
		self.set_class(classtitle)
		self._master.bind('<FocusIn>', self.focus_in)

	@property
	def master(self):
		return self._master

	@master.setter
	def master(self, value):
		self._master = value

	@property
	def parent(self):
		return self._parent

	@parent.setter
	def parent(self, value):
		self._parent = value

	@property
	def child(self):
		return self._child

	@child.setter
	def child(self, value):
		self._child = value

	@property
	def leaf(self):
		leaf = self.child
		while leaf.child is not None:
			leaf = leaf.child

		return leaf

	@property
	def trunk(self):
		trunk = self.parent
		while trunk.parent is not None:
			trunk = trunk.parent

		return trunk

	@property
	def is_destroyed(self):
		return self._destroyed

	def destroy(self, event=None):
		if not self.is_destroyed:
			self.destroy_child()

			try:
				self.master.quit()
				self.master.destroy()
			except TclError:
				pass

			self._destroyed = True

		if self.parent is not None:
			self.parent.child = None

	def set_class(self, classname):
		self.master.wm_iconname(classname)

	def set_title(self, title):
		self.master.wm_title(title)

	def set_size(self, width=None, height=None):
		if width is not None and height is not None:
			self.master.geometry('{}x{}'.format(width, height))

		else:
			(old_width, old_height) = [
				int(x) for x in self.master.geometry().split('+')[0].split('x')
			]

			if width is not None:
				self.master.geometry('{}x{}'.format(width, old_height))

			elif height is not None:
				self.master.geometry('{}x{}'.format(old_width, height))

			#else: # do nothing, nothing specified

	def focus_in(self, event_instance):
		self.focus_child()

	def focus_child(self):
		if self.child is not None and not self.child.is_destroyed:
			self.child.master.lift()
			self.child.master.focus()

	def spawn_child(self, child):
		if self.child is not None:
			self.destroy_child()

		self.child = child
		child.parent = self
		return child.run()

	def destroy_child(self):
		if self.child is not None and not self.child.is_destroyed:
			self.child.destroy()

		self.child = None

	def run(self):
		try:
			self.master.mainloop()
		except KeyboardInterrupt:
			pass

		self.destroy()
		return self._ret
