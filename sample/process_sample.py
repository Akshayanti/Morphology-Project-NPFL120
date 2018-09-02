#! /usr/bin/env python3

import sys

if len(sys.argv) < 3:
	print("You must give at least 2 files to analyze their outputs with the switch.\n"
	      "Switches:\n"
	      "combine : combine the files\n"
	      "coverage : check the coverage of nouns. First file is the source file and the remaining are the files you want to check coverage in.\n"
	      "usage: {} switch input_files".format(sys.argv[0]))
	exit(1)

type_file = None
if len(sys.argv[2].split(".")) >= 2:
	type_file = sys.argv[2].split(".")[1].lower()
switch = sys.argv[1]

def extension_check():
	for i in range(2, len(sys.argv)):
		if sys.argv[i].split(".")[1].lower() != type_file:
			print("All files must be of same type")
			exit(1)
		
if type_file == "most_common" and switch == "combine":
	extension_check()
	from collections import Counter
	counter = Counter()
	outfile = open("sample/sample.most_common", "w")
	for i in range(2, len(sys.argv)):
		with open(sys.argv[i], "r") as infile:
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

if type_file == "most_common" and switch == "coverage":
	extension_check()
	source_list = []
	with open(sys.argv[2], "r") as source:
		contents = source.readlines()
		for lines in contents:
			source_list.append(lines.split(" : ")[0].lower())

	print("#################################################################################")
	for i in range(3, len(sys.argv)):
		dest_list = []
		with open(sys.argv[i], "r") as dest:
			contents = dest.readlines()
			for lines in contents:
				dest_list.append(lines.split(" : ")[0].lower())
		print(sys.argv[i] + " : " + str(len([x for x in source_list if x in dest_list])) + "/" + str(len(source_list)) + "\t" + str(round(len([x for x in source_list if x in dest_list])*100/len(source_list), 4)) + " %")
	print("#################################################################################")


# copied from extract_dict.py
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
							# the tokens without either tag, would be removed from the list, since they are usually Noun-ised versions of other POS tags. Eg- भारतीय (Indian)
							scores[token][2] += 1
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
		print("compares two files, to give the output based on how correct are the values in generated tsv to truth values. Usage:\n"
		      "this_file translation_check file_with_predictions file_with_truth values")
		exit(0)
	truth_val = dict()
	trans = dict()
	outfile = open("sample/truth_data_analysis", "w")
	with open(sys.argv[3], "r") as truth:
		contents = truth.readlines()
		for lines in contents:
			eng, hin, gender = lines.strip("\n").split("\t")
			if hin != "-":
				truth_val[hin] = gender
				if hin not in trans:
					trans[hin] = eng
	std_decisions = ["M", "F"]
	
	with open(sys.argv[2], "r") as prediction:
		contents = prediction.readlines()
		for lines in contents:
			token, male, female, quest, decision = lines.strip("\n").split("\t")
			symbol = ""
			if decision == truth_val[token]:
				symbol = "+"
			else:
				if decision in std_decisions:
					symbol = "-"
				elif decision == "~":
					symbol = "?"
				elif decision[0] == truth_val[token] and decision[1] == "~":
					symbol = "+-"
				elif decision[0] != truth_val[token] and decision[1] == "~":
					symbol = "-~"
			total = int(male) + int(female) + int(quest)
# 	Key:
#   +       Multiple translations, with all gender correct
#   -       Multiple translations, with all gender incorrect
#   ?       Multiple translations, some correct, few incorrect
#   +~      Multiple translations, most correct, some unresolved
#   -~      Multiple translations, most incorrect, some unresolved

			# Output format:
			# Token_eng     Token_hin     Frequency       Male        Female      Questionable        Decision
			outfile.write(trans[token] + "\t" + token + "\t" + str(total) + "\t" + str(male) + "\t" + str(female) + "\t" + str(quest) + "\t" + symbol + "\n")
	outfile.close()
