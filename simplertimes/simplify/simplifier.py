from typing import *

class AbstractSimplifier:
     def simplify_documents(self, documents:Union[List[str], str]) -> Union[List[List[str]], List[List[Tuple[str,str]]]]:
        """Simplifies the documents given. To be implemented by extending classes.
        
        Args:
            documents : str | [str]
                The document(s) to simplify
        
        Returns:
            A list containing the simplified documents. `out[0]` gives the simplified documents.
            `out[1]` gives the complex-simple sentence pairs. Accessing complex-simple pairs will
            follow the format: `pairs[doc_idx][pair_idx][orig=0|simp=1]`
        """
        raise NotImplementedError

from .access_simp import AccessSimplifier
from .depsym_simp import DEPSYMSimplifier

ACCESS = "ACCESS"
DEPSYM = "DEPSYM"
def create_simplifier(simp_type:str) -> AbstractSimplifier:
    """Retuns the specified simplifier"""
    if simp_type == ACCESS:
        return AccessSimplifier()
    if simp_type == DEPSYM:
        return DEPSYMSimplifier()