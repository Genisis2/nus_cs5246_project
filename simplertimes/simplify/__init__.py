# Download for ACCESS tokenization
import nltk
nltk.download('perluniprops')
nltk.download('stopwords')
nltk.download('punkt')

from .simplifier import create_simplifier, AccessSimplifier