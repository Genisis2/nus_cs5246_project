import difflib
import spacy
import operator
from nltk.corpus import wordnet as wn
nlp = spacy.load("en_core_web_lg")

def find_diffs(comp_sentence, simp_sentence):
    ''' find list of diffs'''
    doc_comp = nlp(comp_sentence)
    doc_simp = nlp(simp_sentence)
    d = difflib.Differ()
    diff = d.compare([w.text for w in doc_comp], [w.text for w in doc_simp])
    deleted = []
    replaced = []
    for i,s in enumerate(diff):
        if s[0]=='-':
            word = s[2:]
            for w in doc_comp:
                if w.text==word and not w.is_stop and not w.is_punct:
                    deleted.append(w)
        if s[0]=='+':
            word = s[2:]
            for w in doc_simp:
                if w.text == word and not w.is_stop and not w.is_punct:
                    replaced.append(w)
    return deleted,replaced 

def find_potential_matches(deleted,replaced):
    '''find potential word matches'''
    replaced_pos = [w.pos_ for w in replaced]
    potential_pairs = []
    for del_w in deleted:
        candidate_word = {}
        to_skip = False
        for repl_w in replaced:
            if del_w.lemma_ == repl_w.lemma_:
                #skip this word
                to_skip = True
            elif replaced_pos.count(repl_w.pos_) == 1 and del_w.pos_ == repl_w.pos_:
                potential_pairs.append([del_w, repl_w])
                break
            elif del_w.pos_ == repl_w.pos_: 
                candidate_word[repl_w] = del_w.similarity(repl_w)
        if candidate_word:
            top_similar = sorted(candidate_word.items(), key=operator.itemgetter(1),reverse=True)[0][0]
            potential_pairs.append([del_w, top_similar])
        if not to_skip and not del_w in [item for pair in potential_pairs for item in pair]:
            potential_pairs.append([del_w, None])
    return potential_pairs
    
def eliminate_dupes(potential_pairs, replaced):
    ''' eliminate duplicate matches'''
    matched = [item[1] for item in potential_pairs]
    dupes = {}
    for word in matched:
        indices = [index for index, item in enumerate(matched) if item == word]
        if len(indices) > 1 and not word is None:
            dupes[word] = indices
    for word, indices in dupes.items():
        if replaced.count(word) >= len(indices):
            continue
        similarity_words = [potential_pairs[i][0] for i in indices]
        similarity_scores={}
        for sim_w in similarity_words:
            similarity_scores[sim_w] = sim_w.similarity(word)
        top_similar = sorted(similarity_scores.items(), key=operator.itemgetter(1),reverse=True)[0][0]
        for i in indices:
            if potential_pairs[i][0] != top_similar:
                potential_pairs[i][1] = None
    return potential_pairs
        
    
def get_word_definition(word):
    ''' return word definition from wordnet'''
    syns = wn.synsets(word)
    meaning = None
    if syns:
        meaning = syns[0].definition()
    return meaning