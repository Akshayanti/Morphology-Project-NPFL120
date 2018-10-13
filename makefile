# THIS MAKEFILE IS MEANT FOR LINUX ONLY. HOWEVWER, IT CAN BE MODIFIED AS PER CONVENVIENCE TO BE USED WITH OTHER OS AS WELL.


# LIST OF VARIABLES

# Change here, to the location of folder containing the UDPipe Models
UDPIPE_Models := $(HOME)/udpipe-ud-2.0-170801

# download the corpus, storing it as parallel.tgz. After the download, need to unzip the corpus into the current directory, with the original name preserved.
download:
	wget http://www.cfilt.iitb.ac.in/iitb_parallel/iitb_corpus_download/parallel.tgz --user-agent "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 Chrome/25.0.1364.160 Safari/537.22"
	tar -xf parallel.tgz
	mv parallel/IITB.en-hi.hi ./
	rm -r parallel
	rm parallel.tgz

#	The current folder now contains the downloaded corpus. Edit the variable `$UDPIPE_Models` above to point to udpipe's saved model folders.
#	This step will most likely take a few hours. Please be patient.
#	Output file:	hi.conllu
udpipe_process:
	udpipe --tokenizer=presegmented --tag --parse --immediate $(UDPIPE_Models)/hindi-ud-* IITB.en-hi.hi > hi.conllu

#	After the step above, we have CONLLU format analyzed hi.conllu files.
#	This will extract the list of nouns in a file called en.NOUN and the entries in the CONLLU file with the tag as NOUN, seperated by the line ID.
#	After getting the output, we sort the unique values of the words found, and store them back in the same file.
get_nouns:
	#	The switch at the end of the next two commands is optional, to view the case-insensitive list of the most common nouns, followed by their frequencies, stored in langcode.most_common file.
	# 	Feel free to remove `--count` switch if you don't want to see those statistics. However, it is HIGHLY recommended that you use that switch.
	# 	The two files generated here, .most_common (from --count) and .NOUN (from -pos) differ in their length, since the latter also includes some garbage values.
	# 	By garbage values, it is meant that the values are not of the form in devanagri alphabet or are useless otherwise. So, we eliminate the files with .NOUN
	# 	and also the file with .output since we won't be needing that file for this output
	#	Output file:	hi.most_common; hi.output
	python3 extract_dict.py -i hi.conllu -pos NOUN --count
	rm hi.NOUN

# 	Since, we won't be needing a few files anymore, let's clean up the directory a bit
cleanup:
	mkdir corpus
	mv IITB.en-hi.hi corpus/
	mv hi.conllu corpus/

# 	Having cleaned up the directory, we remove noun tokens from consideration which might be
# 	1. having non-clear usage of gender, i.e. gender can't be defined in particular for the usage at certain times.
# 	2. can be used with either gender
#	The resulting file checked is called remove_list
sample_data:

	#	Download UD treebanks
	curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2837/ud-treebanks-v2.2.tgz -o $(HOME)/
	tar -xf $(HOME)/ud-treebanks-v2.2.tgz
	rm $(HOME)ud-treebanks-v2.2.tgz

	#	Transfer treebanks to another folder for ease of usage, and proecess the CONLLU files contained within.
	mkdir $(HOME)/ud-treebanks-v2x2
	mv $(HOME)/ud-treebanks-v2.2/* $(HOME)/ud-treebanks-v2x2/
	python3 extract_dict.py -i $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-dev.conllu -pos NOUN --count
	python3 extract_dict.py -i $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-test.conllu -pos NOUN --count
	python3 extract_dict.py -i $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-train.conllu -pos NOUN --count
	python3 extract_dict.py -i $(HOME)/ud-treebanks-v2x2/UD_Hindi-PUD/hi_pud-ud-test.conllu -pos NOUN --count

	#	Create a directory and then move the results to this directory
	mkdir sample
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-dev.output sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-dev.NOUN sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-dev.most_common sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-test.output sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-test.NOUN sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-test.most_common sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-train.output sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-train.NOUN sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-train.most_common sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-PUD/hi_pud-ud-test.output sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-PUD/hi_pud-ud-test.NOUN sample/
	mv $(HOME)/ud-treebanks-v2x2/UD_Hindi-PUD/hi_pud-ud-test.most_common sample/
	mv $(HOME)/ud-treebanks-v2x2/* $(HOME)/ud-treebanks-v2.2/
	rm -r $(HOME)/ud-treebanks-v2x2
	rm sample/hi*.NOUN
	mv process_sample.py sample/

	#	Combine the multiple .most_common files, and delete the redundant data.
	python3 filter_data.py --combine sample/hi_*.most_common
	rm sample/hi*.most_common

	#	Check the translations and get Table 1 as in the source paper.

		#	Test to know how many values in the true_gender values are used in different context, and output result in an intermediate file.
		#	Output file: sample/test
	python3 sample/process_sample.py translation true_gender_hin.list sample/*.output > sample/test

		#	Process this intermediate file, to generate the symbols as explained in process_sample.py file as comments to get a similar output to table 1 in the reference paper
		#	Output file: sample/truth_data_analysis
	python3 sample/process_sample.py translation_check sample/test true_gender_eng_to_hin.tsv

		#	Sort the output file, and get rid of the intermediate file
	sort -u sample/truth_data_analysis > sample/default_seeds_table.tsv
	rm sample/test
	rm truth_data_analysis

#	With all the data ready, we start with context bootstrapping on the sample data, to update the seeds
#	and then go for morphological analysis using trie model
bootstrap:

	#	get the list of seeds.
	#	Output file:	seeds.LIST
	python3 filter_data.py -i true_gender_eng_to_hin.tsv -ds

	#	remove seeds, ambiguous content, low freq items from sample/sample.most_common

		#	output file generated:	sample/sample.most_common.list_filtered
	python3 filter_data.py -i sample/sample.most_common -fl -l remove_list
	mv sample/sample.most_common.list_filtered sample/sample.removed

		#	output file generated:	sample/sample.removed.list_filtered > context_bootstrap
	python3 filter_data.py -i sample/sample.removed -fl -l seeds.LIST
	mv sample/sample.removed.list_filtered sample/context_bootstrap
	rm sample/sample.removed

	#	continue with the bootstraping, and updating seeds.LIST
	python3 filter_data.py --bootstrap -i sample/context_bootstrap --conllu sample/hi_*.output

	#	remove all seeds values from non_ambig file, and use it for morphological tagging
	python3 filter_data.py -i sample/context_bootstrap -fl -l seeds.LIST
	mv sample/context_bootstrap.list_filtered sample/morpho

#	With the contextual bootstrapping completed, we move on to morphological analysis using trie model
# 	And finally, we generate the coverage and the final accuracy of the trie based approach.
morphology:
	
	#	morphologically tag all the values in the sample data
	#	output files:	morpho.output, 	morpho.not_analysed
	
	python3 filter_data.py --morphology -i sample/morpho --conllu sample/*.output > sample/morpho.not_analysed
	cat sample/morpho.output >> seeds.LIST

	#	let's start processing the corpus that we initially extracted nouns from

		#	remove all the tokens that are present in remove_list
		#	Output file:	hi.most_common.list_filtered > hi.non-ambig1
	python3 filter_data.py -fl -l remove_list -i hi.most_common
	mv hi.most_common.list_filtered hi.non-ambig1

		#	remove all the tokens that are present in sample/morpho.not_analysed
		#	Output file:	hi.non-ambig1.list_filtered > hi.non-ambig
	python3 filter_data.py -fl -l sample/morpho.not_analysed -i hi.non-ambig1
	mv hi.non-ambig1.list_filtered  hi.non-ambig
	rm hi.non-ambig1

		#	remove all the tokens present in seeds.LIST
		#	Output file:	hi.non-ambig.list_filtered > hi.morph
	python3 filter_data.py -fl -l seeds.LIST -i hi.non-ambig
	mv hi.non-ambig.list_filtered hi.morph
	rm hi.non-ambig

		#	now, let us use the trie model for hi.morph file to get the final output
		#	Output file: hi.morph.output
	python3 filter_data.py --morphology -i hi.morph > hi.morph.not_analysed

	#	Finally, get stats to check how the system performed on the corpus
	python3 filter_data.py --get_accuracy -i hi.morph.output --conllu hi.output
