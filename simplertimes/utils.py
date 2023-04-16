from nltk.tokenize import TreebankWordDetokenizer
import re

"""Utility class for various helpful functions."""

def remove_pegasus_new_line(document:str) -> str:
    """For handling PEGASUS output with <n> newlines"""
    new_doc = re.sub("<n>", " ", document)
    return new_doc

def join_depsym_dash_delimited(text:str) -> str:
    """Joins words that were separated by a dash

    Args:
        text : str
            The source text
    Returns:
        The text with words like `black - and - white` joined to `black-and-white`
    """
    pattern = re.compile(r"\s+-\s+")
    text = pattern.sub(r'-', text)
    return text

def replace_start_quote_for_tb(text:str) -> str:
    """Replaces the starting double quotes with treebank standard ``
    
    Code to find starting double quotes from: https://github.com/nltk/nltk/issues/3006

    Args:
        text : str
            The source text
    Returns:
        The text with starting double quotes replaced for TB detokenization
    """
    # Replace pairs of ''...'' with ``...''
    pattern = re.compile(r"''(.*?'')")
    text = pattern.sub(r'``\1', text)
    return text

def detokenize_for_output(text:str) -> str:
    """Detokenizes and input for proper formatting
    
    Args:
        text : str
            Assumes the tokenized text is one white-space delimited string
    Returns:
        Detokenized text
    """
    # Handling for PEGASUS output of newlines
    text = remove_pegasus_new_line(text)
    # Handling for DEPSYM splitting words that are dash-delimited
    text = join_depsym_dash_delimited(text)
    # Handling of start quotes to align with treebank
    text = replace_start_quote_for_tb(text)
    # Split by space to retrieve token list
    tokens = [ tok for tok in text.split(" ") if tok != "" ]
    # Detokenize
    text = TreebankWordDetokenizer().detokenize(tokens)
    # Detokenizer only handles periods at the end of the text.
    # If text is a paragraph, the in-between periods are untouched.
    # Address that with this regex, modified from the treebank.py 
    # in NLTK for handling of !,?
    text = re.compile(r"\s([\.])").sub(r"\g<1>", text)
    return text
