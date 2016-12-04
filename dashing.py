#!/usr/bin/env python

from tk_dashing import tk_dashing

if __name__ == '__main__':
	try:
		app = tk_dashing()
		app.run()
	except KeyboardInterrupt:
		pass
