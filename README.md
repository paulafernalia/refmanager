# refmanager

**General description**

Generate a bibtex file with based on pdf documents such as books and articles included in a directory.

**How it works?**

Some articles downloaded from online repositories contain the DOI in the metadata. In particular, ScienceDirect seems to generate consistent metadata. This tool will look for this DOI and if it cannot find it, it will try to get the DOI from www.crossref.org through the python API, searching by title. This title will come from the metadata in the PDF, if available, otherwise it will take it from the file name (so it relies on the user having a good file naming convention and discipline to follow it). Once it has all the DOI's it could find, it will convert them to bib entries using http://dx.doi.org/<doi>, it will check that all unique keys are unique and finally it will export all the entries to a single .bib file. Names of files for which a DOI was not found will be exported in a list to a file missing.txt.

**Usage**

*Mode 1*: `python main.py`

It will generate a .bib file reading all pdf files in the current directory.

*Mode2*: `python main.py /path/to/folder/with/pdfs`

It will generate a .bib file reading all pdf files in the directory passed as an argument.

*Mode 3*: `python main.py /path/to/folder/with/pdfs filename.pdf`

It will attempt to generate a .bib file with a single bib entry based on the file passed as the second argument.

**Note**

When neither the DOI or the title are found in the metadata, the tool will look for a title in the filename assuming the following file naming convention was used:

```YYYY - AUTHOR - Title.pdf```



