<h1> Morphology Project </h1>

<h2>About</h2>
This is the morphology project submitted for NPFL096- Computational Morphology coursework, taught by Jirka Hana for 2018 Summer Semester.

The project is an implementation of the [paper](base_paper) [1] on 'Minimally Supervised Induction of Grammatical Gender' for the evaluation of English-Hindi pair.

<h2>Data Resources

1. IIT-B parallel-corpus [2], available for download [here](http://www.cfilt.iitb.ac.in/iitb_parallel/iitb_corpus_download/).
2. [UDPipe](udpipe) [3] for analysis and processing of the parallel-corpus mentioned above.

<h2>Pipeline</h2>

The pipeline of the entire project, as reproducible through the [makefile](makefile) with certain changes, is explained as follows.

1. After the parallel corpus is downloaded and then extracted with their names intact, they are processed with UDPipe, using version 2.0 models. While using UDPipe, be careful to use the `--immediate` and `--tokenizer=presegmented` as arguments, so as to process the files on Hindi side keeping the one-line concurrency between the two files.
2. Having stored the files in [en.conllu](en.conllu) and [hi.conllu](hi.conllu) respectively, we extract all the nouns from each of them using the [extract_dict.py](extract_dict.py)'s `-pos NOUN` switch.


<h2> Files included </h2>

This section includes the files contained, with the switches, if available with their intended purpose.

<h2>References and Citations</h2>

[1] Cucerzan, S., & Yarowsky, D. (2003). [Minimally supervised induction of grammatical gender](base_paper). In Proceedings of the 2003 Conference of the North American Chapter of the Association for Computational Linguistics on Human Language Technology-Volume 1 (pp. 40–47). Association for Computational Linguistics.  

[2] Anoop Kunchukuttan, Pratik Mehta, Pushpak Bhattacharyya. [The IIT Bombay English-Hindi Parallel Corpus](IIT-B). 2017 

[3] UDPIPE

[4]


[base_paper]: https://aclweb.org/anthology/N/N03/N03-1006.pdf
[IIT-B]: http://www.cfilt.iitb.ac.in/iitb_parallel/
[udpipe]: www.example.com
