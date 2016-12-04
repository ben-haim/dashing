#!/usr/bin/env python

#
# Dashing - dashing.py
#
# Author: Brad Cable
# Email: brad@bcable.net
# License: GPLv2
#

from tk_dashing import tk_dashing

if __name__ == '__main__':
	try:
		app = tk_dashing()
		app.run()
	except KeyboardInterrupt:
		pass
