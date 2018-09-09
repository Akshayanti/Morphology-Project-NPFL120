#! /usr/bin/env python3
# coding: utf-8

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type= str, help="Input File", required=False)
parser.add_argument("-ff", "--filter_by_freq", action='store_true', help="Create a version of file with frequency >= \'-f\'", required=False)
parser.add_argument("-f", "--frequency", type=int, help="The threshold frequency below which the tokens need to be deleted", required=False)
parser.add_argument("-fl", "--filter_by_list", action='store_true', help="Create a version of file with tokens from \'-l\' removed", required=False)
parser.add_argument("-l", "--list_file", type=str, help="File with the list of tokens to filter", required=False)
parser.add_argument("--combine", help="combine the files (*.most_common) to a single file, with updated values", nargs="*", required=False)
args = parser.parse_args()

def get_dict(all_contents):
	values = dict()
	for line in all_contents:
		key, value = line.split(" : ")
		values[key] = int(value.strip("\n"))
	return values


def filter_dict(a_dict, all_contents):
	dict_copy = a_dict
	for line in all_contents:
		if line.strip("\n") in dict_copy:
			del dict_copy[line.strip("\n")]
	return dict_copy

if __name__ == "__main__":
	
	if args.filter_by_list:
		items = dict()
		with open(args.input, "r") as infile:
			contents = infile.readlines()
			items = get_dict(contents)
		if not args.list_file:
			print("MISSING ARGUMENT\n"
			      "-l: File with the list of tokens to filter")
			exit(0)
		with open(args.list_file, "r") as listfile:
			contents = listfile.readlines()
			items = filter_dict(items, contents)
		with open(args.input+".list_filtered", "w") as outfile:
			for a in items:
				outfile.write(a + " : " + str(items[a]) + "\n")
	
	if args.filter_by_freq:
		items = dict()
		if not args.frequency:
			print("MISSING ARGUMENT\n"
			      "-f: The threshold frequency below which the tokens need to be deleted")
			exit(0)
		with open(args.input, "r") as infile:
			contents = infile.readlines()
			for line in contents:
				key, value = line.split(" : ")
				if int(value.strip("\n")) >= args.frequency:
					items[key] = int(value.strip("\n"))
		with open(args.input+"_min_"+str(args.frequency), "w") as outfile:
			for a in items:
				outfile.write(a + " : " + str(items[a]) + "\n")
	
	if args.combine:
		from collections import Counter
		counter = Counter()
		outfile = open("sample/sample.most_common", "w")
		for i in range(len(args.combine)):
			with open(args.combine[i], "r") as infile:
				contents = infile.readlines()
				for line in contents:
					word = line.split(" : ")[0].lower()
					value = int(line.split(" : ")[1])
					if word not in counter:
						counter[word] = value
					else:
						counter[word] += value
		counter = counter.most_common()
		for vals in counter:
			outfile.write(vals[0] + " : " + str(vals[1]) + "\n")
		outfile.close()
