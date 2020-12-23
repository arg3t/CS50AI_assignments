import nltk
import sys
import os, string, math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = os.listdir(directory)
    mapping = dict()
    for i in files:
        with open(os.path.join(directory,i), "r") as f:
            mapping[i] = f.read()
    return mapping


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    split = nltk.word_tokenize(document.lower())
    processed = []
    for i in split:
        if i in nltk.corpus.stopwords.words("english"):
            continue
        if  i[0] in string.ascii_lowercase:
            processed.append(i)
    return processed


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    all_words = dict()
    for i in documents.values():
        for j in i:
            if j in all_words:
                continue
            contains = 0
            for k in documents:
                if j in documents[k]:
                    contains += 1
                    continue
            all_words[j] = math.log(len(documents)/contains)
    return all_words



def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    rankings = {}
    for i in files:
        tfidf = 0
        for j in query:
            tf = files[i].count(j)
            tfidf += tf * idfs[j]
        rankings[tfidf] = i

    scores = list(rankings.keys())
    scores.sort(reverse=True)
    top_n = []
    for i in scores[:n]:
        top_n.append(rankings[i])
    return top_n


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    rankings = {}
    for i in sentences:
        idf = 0
        tf_sum = 0
        for j in query:
            tf =  sentences[i].count(j)
            tf_sum += tf
            idf += tf * idfs[j]
        if idf not in rankings:
            rankings[idf] = []
        rankings[idf].append((i, tf))

    scores = list(rankings.keys())
    scores.sort(reverse=True)
    top_n = []
    for i in scores[:n]:
        selected = rankings[i][0][0]
        if len(rankings[i]) != 0:
            max_tf = 0
            for j in rankings[i]:
                if j[1] > max_tf:
                    selected = j[0]
        top_n.append(selected)
    return top_n


if __name__ == "__main__":
    main()
