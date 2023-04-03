from textwrap import dedent
from typing import List, Union
from nltk.tokenize import sent_tokenize
from access.preprocessors import get_preprocessors
from access.resources.prepare import prepare_models
from access.simplifiers import get_fairseq_simplifier, get_preprocessed_simplifier
from access.text import word_tokenize
from access.utils.helpers import yield_lines, write_lines, get_temp_filepath, mute, delete_files

def _tokenize_document(document):
    """Passes the document sentence by sentence to ACCESS's `word_tokenize` preprocessing step"""

    # Split document into sentences
    sentences = sent_tokenize(document, language='english')
    
    # For each sentence, call word_tokenize
    tokenized = []
    for sentence in sentences:
        # TODO: Check if need to remove newlines here
        sentence = word_tokenize(sentence)
        tokenized.append(sentence)

    return tokenized

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
        simplifier = get_fairseq_simplifier(best_model_dir, beam=8)
        simplifier = get_preprocessed_simplifier(simplifier, preprocessors=preprocessors)
        self.simplifier = simplifier

    def __str__(self) -> str:
        return dedent(f"""\
            {self.simplifier}\
            """)
    
    def print_details(self):
        print(self)

    def simplify_document(self, documents:Union[List[str], str], include_source:bool=False) -> List[List[str]]:
        """Simplifies the documents given
        
        Args:
            documents : str | [str]
                The document(s) to simplify
            include_source : bool
                Includes the source documents in the output
        
        Returns:
            A list containing the simplified documents. `out[0]` gives the simplified documents.
            `out[1]` gives the original documents. `out[1]` is only present if `include_source=True`.
        """
        
        # Ensure list
        if isinstance(documents, str):
            documents = [documents]

        # For keeping track of source and prediction files created
        sources = []
        preds = []
        try:
            # Tokenize and put each document into its own file
            # Document will be split into sentences and each tokenized
            # sentence will take up a line in the file
            for document in documents:
                source = get_temp_filepath()
                sources.append(source)
                write_lines(_tokenize_document(document), source)

            # Create simplified predictions
            # Each entry is a file containing the simplified sentences
            # of the source file
            with mute():
                for source in sources:
                    pred = get_temp_filepath()
                    preds.append(pred)
                    self.simplifier(source, pred)

            # Extract the strings from the files
            out = []
            pred_docs = []
            for pred in preds:
                # Join the simplified sentences into a document
                sentences = []
                for sentence in yield_lines(pred):
                    sentences.append(sentence)
                pred_docs.append(' '.join(sentences))
            out.append(pred_docs)

            # Include the source in the output, if requested
            if include_source:
                source_docs = []
                for source in sources:
                    # Join the simplified sentences into a document
                    sentences = []
                    for sentence in yield_lines(source):
                        sentences.append(sentence)
                    source_docs.append(' '.join(sentences))
                out.append(source_docs)

        # Always cleanup any files created
        finally:
            delete_files(sources)
            delete_files(preds)

        return out

def create_simplifier(level:int=5) -> AccessSimplifier:
    return AccessSimplifier(level)
