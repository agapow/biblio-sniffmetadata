#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unpacking mutliple archive files from the commandline.

Stuffit has a commandline interface, but it can only call one file at a time.
This wrapper calls unstuff repeatedly, passing archive passwords and deletion
flags, while extinguishing hung processes.

"""


### IMPORTS

import argparse as ap
from multiprocessing import Process
from os import system


### CONSTANTS & DEFINES

_DEV_MODE = True


### IMPLEMENTATION ### 

def run_with_timeout (func, args=(), kwargs={}, timeout=30):
	"""
	Run callable in seperate process, with an optional timeout.
	
	:Returns:
		A boolean for process completion.
	
	"""
	# XXX: unsure about child processes being killed, like if I call to shell
	it = Process (target=func, args=args, kwargs=kwargs)
	it.start()
	it.join (timeout)
	if it.is_alive():
		it.terminate()
		return False
	else:
		return True


## MAIN ###

def parse_args():
	"""
	Construct the general option parser.
	"""
	op = ap.ArgumentParser (description='Unpacks multiple archives using Stuffit.')
	op.add_argument('--version', action='version', version=__version__)
	
	op.add_argument ('--password', 
		dest='password',
		type=int,
		help='To be used for decoding archives',
		metavar='PASSWORD',
		default=None,
	)
	
	op.add_argument ('--delete',
		dest='delete',
		help='Delete archives after sucessful unpacking',
		action='store_true',
	)
	
	op.add_argument ('--timeout', 
		dest='timeout',
		help='Time limit for unpacking individual files',
		metavar='SECONDS',
		default=30,
	)
	
	op.add_argument('infiles', action="store")
	
	opts = op.parse_args()
	
	## Postconditions & return:
	# TODO: assert infiles
	return opts


def main (infiles, opts):
	for f in infiles:
		password = delete = ''
		if opts.password:
			password = '-p "%s"' % opts.password
		if opts.delete:
			delete = '-D'
		cmdline = 'stuff %s %s "%s"' % (password, delete, f)
		run_with_timeout (system, args=[cmdline], timeout=timeout)
	
	
	

if __name__ == '__main__':
	try:
		opts = parse_args()
		main (opts.infiles, opts)
	except BaseException, err:
		if (_DEV_MODE):
			raise
		else:
			print err
	except:
		print "An unknown error occurred.\n"


### END #######################################################################
