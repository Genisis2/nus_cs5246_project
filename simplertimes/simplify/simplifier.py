from textwrap import dedent
from typing import List, Tuple, Union
from nltk.tokenize import sent_tokenize
from access.preprocessors import get_preprocessors
from access.resources.prepare import prepare_models
from access.simplifiers import get_fairseq_simplifier, get_preprocessed_simplifier
from access.text import word_tokenize
from access.utils.helpers import yield_lines, write_lines, get_temp_filepath, mute, delete_files

def _tokenize_document(document):
    """Passes the document sentence by sentence to ACCESS's `word_tokenize` preprocessing step
    
    Args:
        document : str
            A string representing a document to simplify
    Returns:
        The tokenized document for ACCESS input at `out[0]`. The list of sentences of the document
        in `out[1]`.
    """

    # Split document into sentences using NLTK
    doc_sents = sent_tokenize(document, language='english')
    
    # For each sentence,
    tokenized = []
    for sent in doc_sents:
        # Tokenize with the ACCESS provided tokenizer
        tokenized.append(word_tokenize(sent))

    return tokenized, doc_sents

def _get_simplification_params(level:int):
    """Get the simplification parameters of the model for the specified level"""

    # TODO: Do this properly. This is just a placeholder now.
    simplification_params = {
        'LengthRatioPreprocessor': {'target_ratio': 0.95},
        'LevenshteinPreprocessor': {'target_ratio': 0.75},
        'WordRankRatioPreprocessor': {'target_ratio': 0.75},
        'SentencePiecePreprocessor': {'vocab_size': 10000},
    }

    return simplification_params

class AccessSimplifier:
    """Abstraction wrapper around the ACCESS simplifier model"""
    
    def __init__(self, level:int=5):
        """Initializes the model to use
        Args:
            level : int
                The level of simplification to be performed
        """
        # Set simplification arguments appropriate for the user's level
        simp_params = _get_simplification_params(level)
        preprocessors = get_preprocessors(simp_params)

        # Download parameters for the best model from the authors
        best_model_dir = prepare_models()

        # Build simplifier model
        # num_workers=0 to prevent multithreaded error in Windows
        simplifier = get_fairseq_simplifier(best_model_dir, beam=8, num_workers=0)
        simplifier = get_preprocessed_simplifier(simplifier, preprocessors=preprocessors)
        self.simplifier = simplifier

    def __str__(self) -> str:
        return dedent(f"""\
            {self.simplifier}\
            """)
    
    def print_details(self):
        print(self)

    def simplify_document(self, documents:Union[List[str], str]) -> Union[List[List[str]], List[List[Tuple[str,str]]]]:
        """Simplifies the documents given
        
        Args:
            documents : str | [str]
                The document(s) to simplify
        
        Returns:
            A list containing the simplified documents. `out[0]` gives the simplified documents.
            `out[1]` gives the complex-simple sentence pairs. Accessing complex-simple pairs will
            follow the format: `pairs[doc_idx][pair_idx][orig=0|simp=1]`
        """
        
        # Ensure list
        if isinstance(documents, str):
            documents = [documents]

        # For keeping track of source and prediction files created
        # For clean up later
        sources = []
        preds = []
        try:

            # Keep track of the original sentences
            orig_sents = []
            # Pre-process each document for ACCESS
            for document in documents:
                # Get temp file
                source = get_temp_filepath()
                sources.append(source)            
                # Document will be split into sentences and each tokenized
                # sentence will take up a line in the file
                tokenized, doc_sents = _tokenize_document(document)
                write_lines(tokenized, source)
                # Keep track of split sentences
                orig_sents.append(doc_sents)

            # Create simplified predictions
            with mute():
                # For each document
                for source in sources:
                    # Get predicted simplified sentences
                    pred = get_temp_filepath()
                    preds.append(pred)
                    self.simplifier(source, pred)

            # Extract the strings from the output
            simp_docs = []
            simp_sents = []
            for pred in preds:
                # Get the simplified sentences of the document
                sentences = []
                for sentence in yield_lines(pred):
                    sentences.append(sentence)
                # Join the simplified sentences into a simplified document
                simp_docs.append(' '.join(sentences))
                # Keep track of simplified sentences
                simp_sents.append(sentences) 
                
            # Create complex-simple sentence pairs
            orig_simp_pairs = []
            # For each doc that was processed
            for doc_idx in range(len(documents)):
                # Get all the orig and simplified sentences
                doc_orig_sents = orig_sents[doc_idx]
                doc_simp_sents = simp_sents[doc_idx]
                # Store as pair
                orig_simp_pairs.append([ (doc_orig_sents[sent_idx], doc_simp_sents[sent_idx]) 
                                        for sent_idx in range(len(orig_sents)) ])

        # Always cleanup any files created
        finally:
            delete_files(sources)
            delete_files(preds)

        return simp_docs, orig_simp_pairs

def create_simplifier(level:int=5) -> AccessSimplifier:
    return AccessSimplifier(level)
