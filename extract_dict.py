#! /usr/bin/env python3

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i1", "--input1", type= argparse.FileType('r'), help="Input File 1", required=True)
parser.add_argument("-l1", "--language1", type=str, help="Language Code for input1 file", required=False)
parser.add_argument("-i2", "--input2", type= argparse.FileType('r'), help="Input File 2", required=True)
parser.add_argument("-l2", "--language2", type=str, help="Language Code for input2 file", required=False)
parser.add_argument("--pos", "--pos_tag", type=str, help="POS tag to extract", required=False)
args = parser.parse_args()

# GET INDIVIDUAL LINES WITH POS_TAGS HERE, AND THE TOKENS WITH THEIR ROOT GETS PRINTED
def process_conllu(line):
	if line != '\n':
		if line[0] == "#":
			contents = line.split(" = ")
			if contents[0] == "# sent_id":
				text = "ID: " + contents[1].strip("\n")
				return text
			else:
				return ""
		else:
			contents = line.split("\t")
			if contents[3] == args.pos_tag:
				print(contents[1] + "\t" + contents[2])
				return line
			else:
				return ""
	else:
		return "\n"

with open(args.input1) as ip1:
	lines = ip1.readlines()
	with open("{}.output".format(args.input1.split(".")[0]), "w") as out1:
		for line in lines:
			out1.write(process_conllu(line))

with open(args.input2) as ip2:
	lines = ip2.readlines()
	with open("{}.output".format(args.input2.split(".")[0]), "w") as out2:
		for line in lines:
			out2.write(process_conllu(line))
			

