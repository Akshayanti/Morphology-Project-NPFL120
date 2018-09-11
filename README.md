<h1> Morphology Project </h1>

<h2>About</h2>
This is the morphology project submitted for NPFL096- Computational Morphology coursework, taught by Jirka Hana for 2018 Summer Semester.

The project is an implementation of the [paper](base_paper) [1] on 'Minimally Supervised Induction of Grammatical Gender' for the evaluation of English-Hindi pair.

<h2>Data Resources</h2>

1. IIT-B parallel-corpus [2], available for download [here](http://www.cfilt.iitb.ac.in/iitb_parallel/iitb_corpus_download/).
2. [UDPipe](udpipe) [3] for analysis and processing of the parallel-corpus mentioned above.
3. Google's pygtrie Python library [4]. 
4. UD 2.x Treebanks for Hindi Language [5].

<h2>Pipeline</h2>

The pipeline of the entire project, as reproducible through the [makefile](makefile) with certain changes, is explained as follows. The section headings give an overview of makefile targets that achieve the mentioned process.  

<h3>`udpipe_process`, `get_nouns`</h3>

1. After the parallel corpus is downloaded and then extracted with their names intact, they are processed with UDPipe, using version 2.0 models. 
While using UDPipe, be careful to use the `--immediate` and `--tokenizer=presegmented` as arguments, so as to process the files on Hindi side keeping the one-line concurrency between the two files.  
2. Having stored the processed files in `hi.conllu` file, we extract all the nouns from each of them using the [extract_dict.py](extract_dict.py)'s `-pos NOUN --count` switch, which also gives `hi.most_common` file along with not-needed `hi.NOUN` file.

<h3>`sample_data`</h3>

1. We now get a smaller corpus. In this case, using the UD Treebanks [5], and extract all nouns from the pre-processed conllu files again using [extract_dict.py](extract_dict.py)'s `-pos NOUN --count` switch, their usages in `.output` files and again get rid of `*.NOUN` files obtained.
2. We combine different `.most_common` files using [filter_data.py](filter_data.py)'s `--combine` switch, making sure the final file `sample.most_common` has the counters combined from different `.most_common` files.
3. Next, we generate the values as in Table 1 of the paper for the true gender nouns in Hindi language, using [process_sample.py](process_sample.py)'s `translation` and `translation_check` arguments, thus generating the resulting file called [default_seeds_table.tsv](default_seeds_table.tsv).
The format of this file is explained [here](#table-1).

<h3>`bootstrap`</h3>

Having generated all the needed data, we start with contextual bootstrapping.  
1. First, we generate a file containing the list of seeds, from [true_gender_eng_to_hin.tsv](true_gender_eng_to_hin.tsv) file, using [filter_data.py](filter_data.py)'s  `-ds` switch, getting `seeds.LIST` file.
2. We generate a list of words that are to be removed. This list ([remove_list](remove_list)) is manually compiled and removes the following cases:
    1. words which are in non-devanagri script
    2. words which can be used for both male/female translations.
    3. numbers
    4. words which are transcribed version of English words, and don't undergo the morphology of the hindi language.  
3. Next, we remove all the tokens from `sample.most_common` file which also appear in [remove_list](remove_list) file or `seeds.LIST` file using [filter_data.py](filter_data.py)'s `-fl -l` switches. The resulting file is called `context_bootstrap`. 
4. For context bootstraping, we get the usage information from the different `.output` files generated from the UD treebanks, and consider only the tokens with count >= 4.
5. Once a token shows high enough confidence value with enough information about the relative distribution of the gender distribution, we update the `seeds.LIST` file with the token and the discovered gender.
6. Next, we filter `context_bootstrap` file again with the updated `seeds.LIST` file as in step 3 above. We call this resulting file `morpho` and serves as input for the next step of the pipeline.

<h3>`morphology`</h3>

1. We use trie model using the <b>PYTHON LIBRARY</b> [4] and process the tokens in `morph` file to get the values with confirmed values in `morpho.output` using [filter_data.py](filter_data.py)'s `--morphology --conllu` switches. The tokens that could not be disambiguated based on morphology, are stored in `morpho.not_analysed` file. The `--conllu` switch is used to input certain values with special parameters in the trie. More about this can be read in-file documentation of [filter_data.py](filter_data.py) file.
2. The values in `morpho.output` are concatenated to `seeds.LIST` file again, to update the latter.
3. We next go back to `hi.output` file we had from the first part of the pipeline, and filter the tokens appearing in `seeds.LIST`, `morpho_not_analysed` or [remove_list](remove_list) file, calling the resulting file `hi.morph`.
4. We again process the resulting file without using context bootstraping, and directly use it for morphological analysis, using [filter_data.py](filter_data.py)'s `--morphology` switch, and WITHOUT using `--conllu` switch, treating all the values equally.
5. The confirmed values are again stored with their output gender tags in `hi.morph.output` file, while the ones not-analyzed are stored in `hi.morph.not_analysed` file.
6. Finally, the true_gender values in `hi.morph` file are found using `--get_accuracy --conllu` switch and the accuracy is computed against the predictions found in `hi.morph.output` file with the bootstrapped values. The results are presented [here](#statistics) 

<h2> Files included </h2>

This section includes the files contained, with the switches, if available with their intended purpose.

1. extract_dict.py
2. filter_data.py
3. makefile
4. process_sample.py
5. remove_list
6. true_gender_eng_to_hin.tsv
7. true_gender_hin.list


Note for [true_gender_eng_to_hin.tsv](true_gender_eng_to_hin.tsv) file:
1. Generated from https://www.collinsdictionary.com/us/dictionary/english-hindi
2. In case the word was found to be not common, not included.
3. If a translation was not present, added after checking other resources.
4. Overlaps between the translations, as clear cut not defined.
5. A lot of translations also serve as proper nouns, so might have been removed then, or errorenously tagged that way.
6. Instead of using `gentleman` and `lady` as in paper, `sir` and `madam` was used instead.

<h2>Table 1</h2>

A table of statistics similar to Table 1 in the source paper can be found in [this](default_seeds_table.tsv) file. The following is the structure of the file:

        Token_eng   Token_hin   Frequency   Male    Female  Quest   Key

`Token_eng`:    An English translation of the natural-gender word.  
`Token_hin`:    The token with the english translation in previous field.  
`Frequency`:    Total number of times the token appeared.  
`Male`:         Number of times the token was used in Masculine context.  
`Female`:       Number of times the token was used in Feminine context.  
`Quest`:        Number of times the token was used without specific gender based context.  
`Key`:          Possible values are as follows:

        +       Multiple translations, with all gender correct
        -       Multiple translations, with all gender incorrect
        ?       Multiple translations, some correct, some incorrect
        +~      Multiple translations, most correct, some unresolved
        -~      Multiple translations, most incorrect, some unresolved
     
<h2>Statistics</h2>

<h4>Smaller Corpus</h4>

Extracted Tokens:     8829  
Tokens removed:         931
Effective number of tokens:     7954

Natural-gender seeds:   106  
Used seeds:             59  
Coverage:   Used Seeds * 100 / Effective number of tokens = 5900/7954 =   0.7417 %

Tokens for context bootstraping (T):    7895  
Tokens succesfully bootstraped  (B):    2887  
Coverage:                   B*100 / T = 36.57 %
     
Tokens before morphoanalysis (TM):     5008    
Tokens successfully analyzed (BM):     4793  
Success Rate:                   BM*100 / TM = 95.70 %

<h4>Main corpus</h4>

Extracted Tokens:   159 447  
Removed Tokens:       7 668

Tokens to process:  151 779  
Tokens processed:   

Total true-gender words (TT):  
Found true-gender words (FF):  
Accuracy (computed):    FF * 100 / TT = 

<h2>References and Citations</h2>

[1] Cucerzan, S., & Yarowsky, D. (2003). [Minimally supervised induction of grammatical gender](base_paper). In Proceedings of the 2003 Conference of the North American Chapter of the Association for Computational Linguistics on Human Language Technology-Volume 1 (pp. 40–47). Association for Computational Linguistics.  

[2] Anoop Kunchukuttan, Pratik Mehta, Pushpak Bhattacharyya. [The IIT Bombay English-Hindi Parallel Corpus](IIT-B). 2017 

[3] [UDPipe project](udpipe), maintained by UFAL, Charles University, Prague.

[4] Google's pygtrie library, implementing trie-structures. Available on GitHub [here](pygtrie). 

[5] Treebanks for UDPipe Version 2.x available [here](treebank). Date of last access: August 25, 2018.

[base_paper]: https://aclweb.org/anthology/N/N03/N03-1006.pdf
[IIT-B]: http://www.cfilt.iitb.ac.in/iitb_parallel/
[udpipe]: http://hdl.handle.net/11234/1-1702
[treebank]: https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-2837
[pygtrie]: https://github.com/google/pygtrie
