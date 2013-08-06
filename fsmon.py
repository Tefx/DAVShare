#!/usr/bin/env python

import time, os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class EventHandler(FileSystemEventHandler):

	def __init__(self, root):
		super(EventHandler, self).__init__()
		self.root = root
		self.all_path = os.path.join(self.root, "all")

	def gen_dest(self, src):
		path, filename = os.path.split(src)
		user = os.path.split(path)[1]
		return os.path.join(self.all_path, "(Uploaded_by_%s)_%s" % (user, filename))

	def is_top(self, src):
		fake_root, fake_user = os.path.split(os.path.split(os.path.abspath(src))[0])
		if fake_root != self.root.rstrip(os.sep):
			return False
		elif fake_user == "all":
			return False
		else:
			return True

	def on_created(self, event):
		if not self.is_top(event.src_path):
			return
		dest_path = self.gen_dest(event.src_path)
		if os.path.isdir(event.src_path):
			os.mkdir(dest_path)
			subprocess.call(["mount", "--bind", event.src_path, dest_path])
		else:
			os.link(event.src_path, dest_path)

	def on_moved(self, event):
		if not self.is_top(event.src_path):
			return
		old_dest_path = self.gen_dest(event.src_path)
		dest_path = self.gen_dest(event.dest_path)
		if os.path.isdir(old_dest_path):
			subprocess.call(["umount", old_dest_path])
		if os.path.split(event.dest_path)[0] == os.path.split(event.src_path)[0]:
			os.rename(old_dest_path, dest_path)
			if os.path.isdir(dest_path):
				subprocess.call(["mount", "--bind", event.dest_path, dest_path])

	def on_deleted(self, event):
		if not self.is_top(event.src_path):
			return
		dest_path = self.gen_dest(event.src_path)
		if os.path.isdir(dest_path):
			subprocess.call(["umount", dest_path])
			os.rmdir(dest_path)
		elif os.path.exists(dest_path):
			os.unlink(dest_path)


class Monitor(object):
	def __init__(self, root):
		self.event_handler = EventHandler(root)
		self.observer = Observer()
		self.observer.schedule(self.event_handler, root, True)

	def loop(self):
		self.observer.start()
		try:
			while True:
				time.sleep(5)
		except KeyboardInterrupt:
			self.observer.stop()
		self.observer.join()


if __name__ == '__main__':
	from sys import argv
	Monitor(argv[1]).loop()