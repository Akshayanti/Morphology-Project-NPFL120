#! /usr/bin/env python3

import sys

if len(sys.argv) < 2:
	print("Use \'-h\' or \'--help\' to see script's purpose.\n"
	      "Give the file name as the first parameter otherwise.")
	exit(1)

if sys.argv[1] == "-h" or sys.argv[1] == "--help":
	print("This script is to ")  # TODO: Enter detals here
	exit(1)
