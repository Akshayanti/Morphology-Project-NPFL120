# THIS MAKEFILE IS MEANT FOR LINUX ONLY. HOWEVWER, IT CAN BE MODIFIED AS PER CONVENVIENCE TO BE USED WITH OTHER OS AS WELL.


# LIST OF VARIABLES

# Change here, to the location of folder containing the UDPipe Models
UDPIPE_Models := $(HOME)/udpipe-ud-2.0-170801

# download the corpus, storing it as parallel.tgz. After the download, need to unzip the corpus into the current directory, with the original name preserved.
download:
	wget http://www.cfilt.iitb.ac.in/iitb_parallel/iitb_corpus_download/parallel.tgz --user-agent "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.22 (KHTML, like Gecko) Ubuntu Chromium/25.0.1364.160 Chrome/25.0.1364.160 Safari/537.22"
	tar -xf parallel.tgz
	mv parallel/IITB.en-hi.en ./
	mv parallel/IITB.en-hi.hi ./
	rm -r parallel
	rm parallel.tgz

#The current folder now contains the downloaded corpus. Edit the variable `$UDPIPE_Models` above to point to udpipe's saved model folders.
#This step will most likely take a few hours. Please be patient.
udpipe_process:
	udpipe --tokenizer=presegmented --tag --parse --immediate $(UDPIPE_Models)/english-ud-* IITB.en-hi.en > en.conllu
	udpipe --tokenizer=presegmented --tag --parse --immediate $(UDPIPE_Models)/hindi-ud-* IITB.en-hi.hi > hi.conllu

# After the step above, we have CONLLU format analyzed {en, hi}.conllu files. We need to extract the list of nouns, and get the nouns from both the sources, to get the translations.
#	This will extract the list of nouns in a file called en.NOUN and the entries in the CONLLU file with the tag as NOUN, seperated by the line ID.
#	After getting the output, we sort the unique values of the words found, and store them back in the same file.
get_nouns:
	# The switch at the end of the next two commands is optional, to view the case-insensitive list of the most common nouns, followed by their frequencies, stored in langcode.mostcommon file.
	# Feel free to remove `--count` switch if you don't want to see those statistics. However, it is HIGHLY recommended that you use that switch.
	python3 extract_dict.py -i en.conllu -l en -pos NOUN --count
	python3 extract_dict.py -i hi.conllu -l hi -pos NOUN --count
	rm hi.NOUN
	rm en.NOUN
	# The two files generated here, .most_common (from --count) and .NOUN (from -pos) differ in their length, since the latter also includes some garbage values.
	# By garbage values, it is meant that the values are not of the form in devanagri alphabet or are useless otherwise. So, we eliminate the files with .NOUN

# Since, we won't be needing a few files anymore, let's clean up the directory a bit
cleanup:
	mkdir corpus
	mv IITB.en-hi.en corpus/
	mv IITB.en-hi.hi corpus/
	mv en.conllu corpus/
	mv hi.conllu corpus/

# Having cleaned up the directory, we remove noun tokens from consideration which might be
# 1. having non-clear usage of gender, i.e. gender can't be defined in particular for the usage at certain times.
# 2. can be used with either gender
sample_data:

	# Download UD treebanks
#	curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2837/ud-treebanks-v2.2.tgz -o $(HOME)/
#	tar -xf $(HOME)/ud-treebanks-v2.2.tgz
#	rm $(HOME)ud-treebanks-v2.2.tgz

	# Transfer treebanks to another folder for ease of usage, and proecess the CONLLU files contained within.
	mkdir $(HOME)/ud-treebanks-v2x2
	mv $(HOME)/ud-treebanks-v2.2/* $(HOME)/ud-treebanks-v2x2/
	python3 extract_dict.py -i $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-dev.conllu -pos NOUN --count
	python3 extract_dict.py -i $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-test.conllu -pos NOUN --count
	python3 extract_dict.py -i $(HOME)/ud-treebanks-v2x2/UD_Hindi-HDTB/hi_hdtb-ud-train.conllu -pos NOUN --count
	python3 extract_dict.py -i $(HOME)/ud-treebanks-v2x2/UD_Hindi-PUD/hi_pud-ud-test.conllu -pos NOUN --count

	# Create a directory and then move the results to this directory
#	mkdir sample
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
#	mv process_sample.py sample/
	rm sample/hi*.NOUN

	# Combine the multiple .most_common files, and delete the redundant data. Check the coverage of the data.
	python3 sample/process_sample.py combine sample/hi_*.most_common
	rm sample/hi*.most_common
	python3 sample/process_sample.py coverage sample/sample.most_common hi.most_common

	# test to know how many values in the true_gender values are used in different context, and output result in an intermediate file.
	python3 sample/process_sample.py translation sample/true_gender_hin.list sample/*.output > sample/test

	# process this intermediate file, to generate the symbols as explained in README.md to get a similar output to table 1 in the reference paper
	python3 sample/process_sample.py translation_check sample/test sample/true_gender_eng_to_hin.tsv
	# sort the output file, and get rid of the intermediate file
	sort sample/truth_data_analysis > sample/truth.final
	rm sample/truth_data_analysis
	rm sample/test
	mv sample/truth.final sample/truth_data_analysis.tsv


# TODO: After generating a list of alignements, and eliminating unwanted nouns, find the most suitable collection of nouns, with their translations also good enough in frequency.
# TODO: Check for filenames, and if modifying them, do so in README and this makefile as well.
