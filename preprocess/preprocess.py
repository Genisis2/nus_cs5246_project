import re

def removePegasusNewLine(document):
    new_doc = re.sub("<n>", " ", document)
    return new_doc

def movePeriod(document):
    new_doc = re.sub(' \.', '.', document)
    new_doc = re.sub(' \?', '?', new_doc)
    new_doc = re.sub(' \!', '!', new_doc)
    return new_doc


def pegasusToBart(document):
    return movePeriod(removePegasusNewLine(document=document))

