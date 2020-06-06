from os import getcwd, listdir
from os.path import isfile, join
from PyPDF2 import PdfFileReader
import sys
import urllib.request
from urllib.error import HTTPError
from difflib import SequenceMatcher
from habanero import Crossref

# TODO(paula): deal with duplicate bibkeys


def similar(a, b):
    ''' Estimate the similarity between two strings'''
    return SequenceMatcher(None, a, b).ratio()


def get_pdf_files(path):
    ''' Get all pdf files found in path'''
    files = [f for f in listdir(path) if isfile(join(path, f)) and 'pdf' in f]

    return files


def valid_title(title):
    ''' Check if an article title is valid in length and content'''

    valid = (title is not None) and \
            (len(title) > 20) and \
            (sum(c.isdigit() for c in title) / len(title) < 0.1)
            
    return valid


def get_doi(path, file):
    ''' Get the DOI of an article by searching the metadata or the filename '''

    filepath = join(path, file)

    with open(filepath, 'rb') as f:
        # Get metadata found in the pdf file
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()

        # If doi is found in the metadata
        if '/doi' in info.keys():
            print('(Found by DOI in metadata)     ', file[:50], '...')

            # We found the DOI, we can stop here
            return info['/doi']

        # Otherwise, if title is found in the metadata and it is valid
        if '/Title' in info.keys() and valid_title(info.title):
            search_title = info.title
            metadata = True

        # Otherwise, get title from the file name
        # Assumes filename is '<year> - <author> - <title>.pdf'
        else:
            temp = file[file.find('-')+2:-4]
            search_title = temp[temp.find('-')+2:]
            metadata = False

        # Query crossref API by title
        cr = Crossref()
        results = cr.works(query=search_title)

        # Look for a match in all the results returned
        for item in results['message']['items']:

            if 'title' in item.keys():

                # Check the similarity between this result and the article at hand
                similarity = similar(search_title, item['title'][0], )

                # If they are very similar, then it's probably the same article
                if similarity > 0.8:
                    if metadata:
                        print('(Found by title in metadata)   ', file[:50], '...')
                    else:
                        print('(Found by title in filename)   ', file[:50], '...')

                    # Found a match, return the doi
                    return item['DOI']

        # If we reach this line, we didn't find anything, will return None
        print('(Query did not return anything)', file[:50], '...')


def separate_dois_and_errors(path, files):
    ''' 
    Given a list of files, return a list of valid DOIs and a list of the files
    for which no matching articles were found in the databases
    '''

    error_files = []
    dois = []

    for f in files:

        result = get_doi(path, f)

        if result is None:
            error_files.append(f)
        else:
            dois.append(result)

    return dois, error_files


def doi_to_bib(doi):
    ''' 
    Convert a doi to a bibtex entry searching in 'http://dx.doi.org/' 
    '''
    req = urllib.request.Request('http://dx.doi.org/' + doi)
    req.add_header('Accept', 'application/x-bibtex')
    try:
        with urllib.request.urlopen(req) as f:
            bibtex = f.read().decode()
    except HTTPError as e:
        if e.code == 404:
            print('DOI not found.')
        else:
            print('Service unavailable.')
        sys.exit(1)

    return bibtex


def main():

    # Default path current directory
    try:
        dirpath = sys.argv[1]
    except:
        dirpath = getcwd()

    try:
        #Use this file only
        pdf_files = [sys.argv[2]]
    except:
        # Get list of pdf files in directory
        pdf_files = get_pdf_files(dirpath)

    # Get dois from valid metadata and...
    # ...idenfity problematic files
    dois, error_files = separate_dois_and_errors(dirpath, pdf_files)

    # Print valid bib entries to a bib file
    if len(dois) > 0:
        print()
        print('Valid bibtex entries were exported to "out.bib"')

        with open('out.bib', 'w') as f:
            for doi in dois:
                bibtex = doi_to_bib(doi)
                print(bibtex, file=f)

    # Print problematic files to txt file
    if len(error_files) > 0:
        print()
        print('WARNING: some pdf files did not contain a valid doi. See "missing.txt"')
 
        with open('missing.txt', 'w') as f:
            for file in error_files:
                print(file, file=f)

if __name__ == '__main__':
    main()
