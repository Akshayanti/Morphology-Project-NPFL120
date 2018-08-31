#! /usr/bin/env python3

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type= str, help="Input File", required=True)
parser.add_argument("-l", "--language", type=str, help="Language Code for input file", required=True)
parser.add_argument("-pos", "--pos_tag", type=str, help="POS tag to extract", required=False)
parser.add_argument("-c", "--count", action='store_true', required=False)
args = parser.parse_args()

# TODO: Organize the switches according to the pipeline, to make it more streamlined.

# GET INDIVIDUAL LINES WITH POS_TAGS HERE, AND THE TOKENS WITH THEIR ROOTS
def process_conllu(line):
	if line != '\n':
		if line[0] == "#":
			contents = line.split(" = ")
			if contents[0] == "# sent_id":
				text = "ID: " + contents[1].strip("\n") + "\n"
				return text
			else:
				return ""
		else:
			contents = line.split("\t")
			if contents[3] == args.pos_tag:
				return contents[1]+"\t"+contents[2], line
			else:
				return ""
	else:
		return "\n"

if __name__ == "__main__":
	if args.pos_tag is not None:
		if args.input.split(".")[1].lower() != "conllu":
			print("If using -pos switch, the input file must be a conllu format file, ending with `.conllu`")
			exit(0)
		out_list1 = open("{}.{}".format(args.input.split(".")[0], args.pos_tag), "w")
		with open(args.input, 'r') as ip1:
			lines = ip1.readlines()
			with open("{}.output".format(args.input.split(".")[0]), "w") as out1:
				for line in lines:
					if len(process_conllu(line)) == 2:
						out_list1.write(process_conllu(line)[0]+"\n")
						out1.write(process_conllu(line)[1])
					else:
						out1.write(process_conllu(line))
	
	if args.count:
		from collections import Counter
		counter = Counter()
		if args.pos_tag is None:
			with open(args.input, 'r') as counts:
				values = counts.readlines()
				for vals in values:
					word, root = vals.split("\t")
					if word in counter:
						counter[word] += 1
					else:
						counter[word] = 1
		else:
			with open("{}.{}".format(args.input.split(".")[0], args.pos_tag), "r")  as counts:
				values = counts.readlines()
				for vals in values:
					word, root = vals.split("\t")
					if word.lower() in counter:
						counter[word.lower()] += 1
					else:
						counter[word.lower()] = 1
		counter = counter.most_common()
		with open("{}.most_common".format(args.language), "w") as stats:
			for vals in counter:
				stats.write(vals[0] + " : "+str(vals[1])+"\n")
