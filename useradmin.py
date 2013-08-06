#!/usr/bin/env python

import subprocess
import os

# TEMPLATE = """
# <Location /webdav/%s>
# 	<Limit GET OPTIONS PROPFIND>
# 	require valid-user
# 	</Limit>
# 	<LimitExcept GET OPTIONS PROPFIND>
# 	require user %s
# 	require user admin
# 	</LimitExcept>
# </Location>

# <Location /webdav/%s/all>
# 	<Limit GET OPTIONS PROPFIND>
# 	require valid-user
# 	</Limit>
# 	<LimitExcept GET OPTIONS PROPFIND>
# 	require user admin
# 	</LimitExcept>
# </Location>
# """

class UserCenter(object):
	def __init__(self, authfile, root, all_path, conf_dir="/etc/apache2/webdav_users/"):
		self.authfile = authfile
		self.root = root
		self.all_path = all_path
		self.conf_dir = conf_dir

	def list(self):
		with open(self.authfile, "r") as f:
			for line in f:
				yield line.split(":")[0]

	def add(self, username, passwd=None):
		self.chpasswd(username, passwd)
		home = os.path.join(self.root, username)
		if not os.path.exists(home):
			os.mkdir(home)
			subprocess.call(["chown", "www-data", home])
		all_mirror = os.path.join(home, "all")
		os.mkdir(all_mirror)
		subprocess.call(["mount", "--bind", self.all_path, all_mirror])
		# self.gen_Apache_config(username)

	def delete(self, username):
		home = os.path.join(self.root, username)
		all_mirror = os.path.join(home, "all")
		subprocess.call(["htpasswd", "-D", self.authfile, username])
		subprocess.call(["umount", all_mirror])
		os.rmdir(all_mirror)
		os.rmdir(home)
		# os.remove(os.path.join(self.conf_dir, "%s.conf" % username))

	def chpasswd(self, username, passwd=None):
		if not passwd:
			subprocess.call(["htpasswd", self.authfile, username])
		else:
			subprocess.call(["htpasswd", "-b", self.authfile, username, passwd])

	# def gen_Apache_config(self, username):
	# 	file_name = os.path.join(self.conf_dir, "%s.conf" % username)
	# 	with open(file_name, "w") as f:
	# 		f.write(TEMPLATE % ((username,) * 3))

	def restart_apache(self):
		subprocess.call(["service", "apache2", "restart"])

if __name__ == '__main__':
	from sys import argv
	import argparse
	parser = argparse.ArgumentParser(description='DAVShare User Admin Tools.')
	parser.add_argument("-a", action='store')
	parser.add_argument("-d", action='store')
	parser.add_argument("-m", action='store')
	parser.add_argument("-p", action='store')
	args = parser.parse_args(argv[1:])

	uc = UserCenter("/etc/apache2/conf.d/.htpasswd", "/var/www/webdav/", "/var/www/webdav/all")

	if args.a:
		uc.add(args.a, args.p)
		uc.restart_apache()
	elif args.d:
		uc.delete(args.d)
		uc.restart_apache()
	elif args.m:
		uc.chpasswd(args.m, args.p)
	else:
		print " ".join(uc.list())

