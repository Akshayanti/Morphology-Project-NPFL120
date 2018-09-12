#! /usr/bin/env python3

import sys

if len(sys.argv) < 3:
	print("You must give at least 2 files to analyze their outputs with the switch.\n"
	      "Switches:\n"
	      "translation : reads input from true_gender file, and checks the gender against trailing CONLLU files for their gender\n"
	      "translation_check : compares two files, to give the output based on how correct are the values in generated tsv to truth values.\n"
	      "usage: {} switch input_files".format(sys.argv[0]))
	exit(1)

switch = sys.argv[1]


# repetitively used in filter_data.py
# gets gender value of a CONLL-U format line
def get_gender(phrase):
	feats = phrase.split("\t")[5].split("|")
	for items in feats:
		if "Gender" in items.split("=")[0]:
			return items.split("=")[1]


if switch == "translation":
	
	if len(sys.argv) < 4:
		print("Need at least 3 arguments. Usage:\n"
		      "this_file switch true_gender_source conllu_files")
	
	source = []
	
	# store the gender true nouns in a list.
	with open(sys.argv[2], "r") as sourcefile:
		contents = sourcefile.readlines()
		for lines in contents:
			source.append(lines.strip("\n"))
	
	# analyse conllu files to update the `scores` defaultdict of [M, F, Q] counts.
	# M= Male, F= Female, Q= Questionable
	from collections import defaultdict
	scores = defaultdict(list)
	for i in range(3, len(sys.argv)):
		with open(sys.argv[i], "r") as conllu:
			lines = conllu.readlines()
			for line in lines:
				if line != "\n":
					if line[:2] != "ID":
						token  = ""
						if line.split("\t")[1].lower() in source:
							token = line.split("\t")[1].lower()
						elif line.split("\t")[2].lower() in source:
							token = line.split("\t")[2].lower()
							
						if token not in scores:
							scores[token] = [0, 0, 0]
							
						if get_gender(line) == "Masc":
							scores[token][0] += 1
						elif get_gender(line) == "Fem":
							scores[token][1] += 1
						else:
							scores[token][2] += 1
							
	# 	with the values generated, write the decisions to stdout.
	for i in scores:
		if i in source:
			male, female, quest = scores[i]
			decision = ""
			if male == 0 and female != 0 and quest == 0:
				decision = "F"
			elif male == 0 and female != 0 and quest != 0:
				decision = "F~"
			elif male != 0 and female == 0 and quest == 0:
				decision = "M"
			elif male != 0 and female == 0 and quest != 0:
				decision = "M~"
			elif male != 0 and female != 0 and quest == 0:
				decision = "~"
			elif male != 0 and female != 0 and quest != 0:
				decision = "~~"
			print(i, male, female, quest, decision, sep="\t")

if switch == "translation_check":
	
	if len(sys.argv) != 4:
		print("Usage:\n"
		      "this_file translation_check file_with_predictions file_with_truth values")
		exit(0)
	
	# this will contain the true_gender, as per the gold-standard
	truth_val = dict()
	# this will contain the english translation of the hindi token, used for final print to stdout.
	trans = dict()
	
	# output file
	outfile = open("sample/truth_data_analysis", "w")
	
	# process the reference value and store in dicts.
	with open(sys.argv[3], "r") as truth:
		contents = truth.readlines()
		for lines in contents:
			eng, hin, gender = lines.strip("\n").split("\t")
			if hin != "-":
				truth_val[hin] = gender
				if hin not in trans:
					trans[hin] = eng
	std_decisions = ["M", "F"]
	
	# open predictions file, and generate a TSV resembling Table 1 in the paper.
	with open(sys.argv[2], "r") as prediction:
		contents = prediction.readlines()
		for lines in contents:
			token, male, female, quest, decision = lines.strip("\n").split("\t")
			symbol = ""
			# if predicted tag == right tag
			if decision == truth_val[token]:
				symbol = "+"
			else:
				#   wrong decision entirely
				if decision in std_decisions:
					symbol = "-"
				# 	if there was no decision
				elif decision == "~":
					symbol = "?"
				# 	if value is correctly tagged as [M, F], but ends with ~ sign
				elif decision[0] == truth_val[token] and decision[1] == "~":
					symbol = "+-"
				# 	if value is incorrectly tagged, and ends with ~ sign
				elif decision[0] != truth_val[token] and decision[1] == "~":
					symbol = "-~"
			total = int(male) + int(female) + int(quest)
# 	Key:
#   +       Multiple translations, with all gender correct
#   -       Multiple translations, with all gender incorrect
#   ?       Multiple translations, some correct, some incorrect
#   +~      Multiple translations, most correct, some unresolved
#   -~      Multiple translations, most incorrect, some unresolved

			# Output format:
			# Token_eng     Token_hin     Frequency       Male        Female      Questionable        Decision
			outfile.write(trans[token] + "\t" + token + "\t" + str(total) + "\t" + str(male) + "\t" + str(female) + "\t" + str(quest) + "\t" + symbol + "\n")
	outfile.close()
