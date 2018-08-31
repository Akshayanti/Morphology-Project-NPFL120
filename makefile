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
	# Feel free to remove `--count` switch if you don't want to see those statistics.
	python3 extract_dict.py -i en.conllu -l en -pos NOUN --count
	python3 extract_dict.py -i hi.conllu -l hi -pos NOUN --count
	sort -u en.NOUN > en.NOUN2
	sort -u hi.NOUN > hi.NOUN2
	rm hi.NOUN
	rm en.NOUN
	mv hi.NOUN2 hi.NOUN
	mv en.NOUN2 en.NOUN

# Since, we won't be needing a few files anymore, let's clean up the directory a bit
cleanup:
	mkdir corpus
	mv IITB.en-hi.en corpus/
	mv IITB.en-hi.hi corpus/
	mv en.conllu corpus/
	mv hi.conllu corpus/

# This is to create a bilingual dictionary using the other details of a token, if at all possible. The output format is explained in the alignments tab in the README.md file.
create_dict:
	python3 filename.py -i1 en.output -l1 en -i2 hi.output -l2 hi
