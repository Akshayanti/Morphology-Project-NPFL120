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

parser.add_argument("-ds", "--get_default_seeds", action='store_true', help="Get the default seeds from the file with true_gender data. Requires \'-i\' argument", required=False)

parser.add_argument("--bootstrap", action='store_true', help="Complete contextual bootstraping step for sample.bootstrap file", required=False)
parser.add_argument("--conllu", nargs="*", help="CONLLU files for bootstraping algorithm", required=False)

args = parser.parse_args()


#   wrapper method for extracting `token : value` format into a dict, with (token, value) as (key, value) pair.
def get_dict(all_contents):
	values = dict()
	for line in all_contents:
		key, value = line.split(" : ")
		values[key] = int(value.strip("\n"))
	return values

#   function used for `--filter_by_list` switch.
#   takes the second file contents, and if element is found in the dict, removes it.
def filter_dict(a_dict, all_contents):
	
	dict_copy = a_dict
	for line in all_contents:
		
		# for files with only the list, eg- remove_list
		if len(line.split("\t")) == 1:
			if line.strip("\n") in dict_copy:
				del dict_copy[line.strip("\n")]
		
		# for files with tsv format, eg- seeds.LIST
		else:
			if line.split("\t")[0] in dict_copy:
				del dict_copy[line.split("\t")[0]]
				
	return dict_copy


#   function to read conllu, and send the line of the token to get_gender().
#   called while using `--bootstrap`
def process_conllu(score_dict):
	for i in range(len(args.conllu)):
		with open(args.conllu[i], "r") as conllu:
			contents = conllu.readlines()
			for line in contents:
				if line != "\n":
					if line[:2] != "ID":
						token  = ""
						if line.split("\t")[1].lower() in score_dict:
							token = line.split("\t")[1].lower()
							if get_gender(line) == "Fem":
								score_dict[token][1] += 1
							elif get_gender(line) == "Masc":
								score_dict[token][0] += 1
							else:
								score_dict[token][2] += 1
	return score_dict

#   updates the seeds, by using contextual bootstrapping.
#   works with confidence values of 0.33 and higher.
#   called when using `--bootstrap`
def update_seeds(dest_file, score_dict):
	#   for every token in the score_dict, we iterate this
	for token in score_dict:
		male, female, quest = score_dict[token]
		total = male + female + quest
		confidence = 1 - quest / total
		
		#   base confidence score = 0.33
		if confidence > 0.33:
			if male == 0 and female != 0:
				dest_file.write(token + "\tF\n")
			elif male != 0 and female == 0:
				dest_file.write(token + "\tM\n")
				
			#   if none of the individual values = 0, work with higher confidence score
			elif confidence > 0.70:
				if male <= 0.85 * female:
					dest_file.write(token + "\tF\n")
				elif female <= 0.85 * male:
					dest_file.write(token + "\tM\n")
					

if __name__ == "__main__":
	
	if args.filter_by_list:
		
		#   check if other necessary arguments are provided for.
		if not args.list_file:
			print("MISSING ARGUMENT\n"
			      "-l: File with the list of tokens to filter")
			exit(0)
		
		#   get contents of the input file into a dict.
		items = dict()
		with open(args.input, "r") as infile:
			contents = infile.readlines()
			items = get_dict(contents)
			
		#   get contents of the second file, and send them to filter_dict() for processing.
		with open(args.list_file, "r") as listfile:
			contents = listfile.readlines()
			items = filter_dict(items, contents)
			
		# 	output the results into the file with `.list_filtered` as a suffix.
		with open(args.input+".list_filtered", "w") as outfile:
			for a in items:
				outfile.write(a + " : " + str(items[a]) + "\n")
	
	if args.filter_by_freq:
		
		#    check if other necessary arguments are provided for.
		if not args.frequency:
			print("MISSING ARGUMENT\n"
			      "-f: The threshold frequency below which the tokens need to be deleted")
			exit(0)
		
		#   if contents of a file are less than the min frequency, discard
		items = dict()
		with open(args.input, "r") as infile:
			contents = infile.readlines()
			for line in contents:
				key, value = line.split(" : ")
				if int(value.strip("\n")) >= args.frequency:
					items[key] = int(value.strip("\n"))
		
		#   write the results in output file.
		with open(args.input+"_min_"+str(args.frequency), "w") as outfile:
			for a in items:
				outfile.write(a + " : " + str(items[a]) + "\n")
	
	if args.combine:
		
		from collections import Counter
		counter = Counter()
		outfile = open("sample/sample.most_common", "w")
		
		#   combine the files, opening each file and updating the counter
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
		
		#   write the results in output file.
		for vals in counter:
			outfile.write(vals[0] + " : " + str(vals[1]) + "\n")
		outfile.close()
		
	if args.get_default_seeds:
		
		#   check if other necessary arguments are provided for.
		if not args.input:
			print("MISSING ARGUMENT\n"
			      "-i:  Input File")
			exit(0)
		
		#   just strip second and third column from the file to get the list of default seeds.
		with open(args.input) as tsvfile:
			contents = tsvfile.readlines()
			with open("seeds.LIST", "w") as outfile:
				for lines in contents:
					if lines.split("\t")[1] != "-":
						outfile.write(lines.split("\t")[1] + "\t" + lines.split("\t")[2].strip("\n") + "\n")
					
	if args.bootstrap:
		
		#   check if other necessary arguments are provided for.
		if not args.input:
			print("MISSING ARGUMENT\n"
			      "-i:  Input File")
			exit(0)
		if not args.conllu:
			print("MISSING ARGUMENT\n"
			      "--conllu:    CONLLU files for bootstraping algorithm")
			exit(0)
		
		#   import from sample.process_sample file
		from sample.process_sample import get_gender
		from collections import defaultdict
		
		#   call update_seeds and update the seeds.LIST file
		seeds_file = open("seeds.LIST", "a")
		with open(args.input) as bootfile:
			contents = bootfile.readlines()
			bootfile_dict = get_dict(contents)
			scores = defaultdict(list)
			for items in bootfile_dict:
				scores[items] = [0, 0, 0]
			scores = process_conllu(scores)
		update_seeds(seeds_file, scores)
