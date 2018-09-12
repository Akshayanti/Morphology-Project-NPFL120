#! /usr/bin/env python3
# coding: utf-8

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", type= str, help="Input File", required=False)

parser.add_argument("-fl", "--filter_by_list", action='store_true', help="Create a version of file with tokens from \'-l\' removed", required=False)
parser.add_argument("-l", "--list_file", type=str, help="File with the list of tokens to filter", required=False)

parser.add_argument("--combine", help="combine the files (*.most_common) to a single file, with updated values", nargs="*", required=False)

parser.add_argument("-ds", "--get_default_seeds", action='store_true', help="Get the default seeds from the file with true_gender data. Requires \'-i\' argument", required=False)

parser.add_argument("--bootstrap", action='store_true', help="Complete contextual bootstraping step for sample.bootstrap file", required=False)
parser.add_argument("--conllu", nargs="*", help="CONLLU files for bootstraping algorithm", required=False)

parser.add_argument("--morphology", action='store_true', help="Create a trie and analyze the words as in Section 2.4 of the paper", required=False)

parser.add_argument("--get_accuracy", action='store_true', help="Get coverage and the accuracy for the generated data", required=False)

args = parser.parse_args()


#   wrapper method for extracting `token : value` format into a dict, with (token, value) as (key, value) pair.
def get_dict(all_contents):
	values = dict()
	for line in all_contents:
		key, value = line.split(" : ")
		values[key] = int(value.strip("\n"))
	return values


#   wrapper method for extracting `token : value` format into a dict, with (token, value) as (key, value) pair.
#   differs from get_dict() in only adding a key if value is >=5.
#   called while using `--bootstrap` and `--morphology`
def get_dict2(all_contents, min_value):
	values = dict()
	for line in all_contents:
		key, value = line.split(" : ")
		if int(value.strip("\n")) >= min_value:
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
					
					
# 	returns the values of the process_conllu() in the form of probability score
#   called when using `--morphology`
def get_probab(scoredict):
	for key in scoredict:
		val_list = scoredict[key]
		total = 0
		for a in val_list:
			total +=  a
		for i in range(len(val_list)):
			val_list[i] = val_list[i] / total
	return scoredict


#   A wrapper function to reverse a string.
#   Used when input-ing values into the trie
def reverse(stringval):
	return stringval[::-1]


#   returns P(gender_j | l_n l_n-1 ... l_i) as per formula in the paper
#   called when using `--morphology`
def P(fullword, word, gen):
	if word in t.keys(shallow=False):
		if gen == "M":
			return t[word][0]
		elif gen == "F":
			return t[word][1]
	else:
		if gen == "M":
			return t[reverse(fullword)][0]
		elif gen == "F":
			return t[reverse(fullword)][1]


#   returns P_node(quest) as per formula in the paper
#   called when using `--morphology`
def P_quest(fullword, word):
	if word in t.keys(shallow=False):
		return t[word][2]
	else:
		return t[fullword][2]


#   returns P^ (gender_j | l_n l_n-1 ... l_i l_i+1) as per formula in the paper
#   recursive call
#   called when using `--morphology`
def p_cap(word, i, gender):
	if i == len(word):
		if gender == "F":
			return t[reverse(word)][1]
		elif gender == "M":
			return t[reverse(word)][0]
	return P(word, reverse(word)[:i], gender) + P_quest(reverse(word), reverse(word)[:i]) * p_cap(word, i+1, gender)


#   function call to calculate the coefficient smoothing for a given word
#   calls p_cap(), P_quest() and P()
#   called when using `--morphology`
def process_word(word, gender):
	i = 0
	return p_cap(word, i, gender)
	

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
			bootfile_dict = get_dict2(contents, 4)
			scores = defaultdict(list)
			for items in bootfile_dict:
				scores[items] = [0, 0, 0]
			scores = process_conllu(scores)
		update_seeds(seeds_file, scores)

	if args.morphology:
		
		#   check if other necessary arguments are provided for.
		if not args.input:
			print("MISSING ARGUMENT\n"
			      "-i:  Input File")
			exit(0)
			
		#   import from sample.process_sample file
		from collections import defaultdict
		from sample.process_sample import  get_gender
		import pygtrie as trie
		
		t = trie.StringTrie()
		
		#   first, add all the seeds
		with open("seeds.LIST", "r") as seeds_file:
			contents = seeds_file.readlines()
			for line in contents:
				word, gender = line.strip("\n").split("\t")
				if gender == "M":
					t[reverse(word)] = [1, 0, 0]
				elif gender == "F":
					t[reverse(word)] = [0, 1, 0]
		
		#   now, input entries from the input file
		with open(args.input, "r") as morpho:
			contents = morpho.readlines()
			
			#   since the value at the end of string is supposed to be probability of a gender as per contextual bootstraping
			#   we bootstrap the values with count >= 4 and input the value as the released value of the process_conllu() function, sent to get_probab() function
			#   for count <= 4, we simply input them as [0, 0, 1] making them all questionable, and relying on just smoothing to get the value.
			if args.conllu:
				allscores_dict = get_dict2(contents, 4)
				
				#   add the words with count <= 3 with the corresponding [0, 0, 1] into the trie.
				for line in contents[::-1]:
					word, count = line.strip("\n").split(" : ")
					if word not in allscores_dict:
						t[reverse(word)] = [0.25, 0.25, .50]
						allscores_dict[word] = [0, 0, 1]
					else:
						break
				
				#   process_conllu() with elements of count >= 4
				scores = defaultdict(list)
				for items in allscores_dict:
					scores[items] = [0, 0, 0]
				scores = process_conllu(scores)
				scores = get_probab(scores)
			
				#   having received the probability scores, add the reversed string with the scores to the trie.
				for key in scores:
					t[reverse(key)] = scores[key]
			
			#   for case when not using context bootstraping, just use all the values as such
			#   and let the relevant information be received from the seeds input.
			else:
				allscores_dict = get_dict(contents)
				for word in allscores_dict:
					t[reverse(word)] = [0.25, 0.25, 0.50]
					
		#   now that we have added all the data, it's now time for recursive algorithm.
		for word in allscores_dict:
			M = process_word(word, "M")
			F = process_word(word, "F")
			t[reverse(word)] = [M, F, 1-M-F]
			
		# 	Get final output values in an output file
		with open("{}.output".format(args.input), "w") as outfile:
			for a in t.keys(shallow=False):
				if reverse(a) in allscores_dict:
					if t[a][0] > 0.55:
						outfile.write(reverse(a) + "\tM\n")
					elif t[a][1] > 0.55:
						outfile.write(reverse(a) + "\tF\n")
					else:
						print(reverse(a) + "\t" + str(t[a]))
						
	if args.get_accuracy:
		
		#   check if other necessary arguments are provided for.
		if not args.input:
			print("MISSING ARGUMENT\n"
			      "-i:  Input File for predictions")
			exit(0)
		if not args.conllu:
			print("MISSING ARGUMENT\n"
			      "--conllu:    CONLLU files for bootstraping algorithm")
			exit(0)
		
		#   get predictions in a dictionary
		predict = dict()
		with open(args.input, "r") as predict_file:
			contents = predict_file
			for line in contents:
				word, gender = line.strip("\n").split("\t")
				predict[word] = gender
		
		#   get truth values using context bootstraping with exact values, and append them to a dictionary
		from collections import defaultdict
		from sample.process_sample import get_gender
		
		scores = defaultdict(list)
		true = dict()
		for word in predict:
			scores[word] = [0, 0, 0]
		scores = process_conllu(scores)
		for items in scores:
			male, female, quest = scores[items]
			if male == 0 and quest == 0 and female != 0:
				true[items] = "F"
			elif female == 0 and quest == 0 and male != 0:
				true[items] = "M"
		
		#   get accuracy
		i = 1
		right = 0
		for word in true:
			if word in predict:
				if predict[true] == true[word]:
					right += 1
			i += 1
		
		# 	print accuracy
		print("Accuracy: " + str(right) + " / " + str(i) + " = " + str(right*100/i) + " %")
