#! /usr/bin/env python3
# coding: utf-8

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type= str, help="Input File", required=True)
parser.add_argument("-pos", "--pos_tag", type=str, help="POS tag to extract", required=False)
parser.add_argument("-c", "--count", action='store_true', help = "Display a count of the unique nouns (Case-insensitive) in output file .most_common", required=False)
args = parser.parse_args()

# TODO: Organize the switches according to the pipeline, to make it more streamlined.
# TODO: Add documentation

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
		if args.input.split(".")[-1].lower() != "conllu":
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
		out_list1.close()
		
	if args.count:
		from collections import Counter
		counter = Counter()
		if args.pos_tag is None:
			# process the file name with pos tag at the end, seperated by a dot.
			with open(args.input, 'r') as counts:
				values = counts.readlines()
				for vals in values:
					word, root = vals.split("\t")
					if word.lower() in counter:
						counter[word.lower()] += 1
					else:
						counter[word.lower()] = 1
		else:
			# automatically, get file name from the conllu file
			with open("{}.{}".format(args.input.split(".")[0], args.pos_tag), "r")  as counts:
				values = counts.readlines()
				for vals in values:
					word, root = vals.split("\t")
					if word.lower() in counter:
						counter[word.lower()] += 1
					else:
						counter[word.lower()] = 1
		counter = counter.most_common()
		with open("{}.most_common".format(args.input.split(".")[0]), "w") as stats:
			for vals in counter:
				stats.write(vals[0] + " : "+str(vals[1])+"\n")
