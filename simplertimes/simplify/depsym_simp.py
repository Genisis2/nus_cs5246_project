"""
This implementation of DEPSYM is copied directly from the code notebook in https://github.com/RakshaAg/DEPSYM.

Some code using StanzaLanguage have been modified as it is no longer supported in spacy-stanza v1.x.x.

SpaCy model is changed to use en_core_web_lg instead of en_core_web_sm

@inproceedings{depsym,
  author = {Chatterjee, Niladri and Agarwal, Raksha},
  title        = {DEPSYM: A Lightweight Syntactic Text Simplification Approach using Dependency Trees},
  booktitle    = {Proceedings of the First Workshop on Current Trends in Text Simplification (CTTS 2021), co-located with SEPLN 2021},
  year         = {2021},
  editor       = {Saggion, Horacio and Štajner, Sanja and Ferrés, Daniel and Kim Cheng Sheang},
  pages        = {42-56},
  month        = {09},
}
"""

import spacy
from spacy import displacy
import stanza
import spacy_stanza
from pattern.en import comparative, superlative, conjugate, INFINITIVE, PRESENT, PAST, FUTURE, pluralize
import truecase
import re
import textstat
import pattern

##### MONKEY PATCH OF PATTERN 3.6.0 #####
# Retrieved from https://github.com/clips/pattern/issues/308#issuecomment-1308344763
import os

from pattern.helpers import decode_string
from codecs import BOM_UTF8

from simplertimes.simplify.simplifier import AbstractSimplifier

BOM_UTF8 = BOM_UTF8.decode("utf-8")
decode_utf8 = decode_string

def _read(path, encoding="utf-8", comment=";;;"):
    """ Returns an iterator over the lines in the file at the given path,
        strippping comments and decoding each line to Unicode.
    """
    if path:
        if isinstance(path, str) and os.path.exists(path):
            # From file path.
            f = open(path, "r", encoding="utf-8")
        elif isinstance(path, str):
            # From string.
            f = path.splitlines()
        else:
            # From file or buffer.
            f = path
        for i, line in enumerate(f):
            line = line.strip(BOM_UTF8) if i == 0 and isinstance(line, str) else line
            line = line.strip()
            line = decode_utf8(line, encoding)
            if not line or (comment and line.startswith(comment)):
                continue
            yield line
    return
# The _read method uses old style of raising StopIteration
# Raising stop iteration breaks the code in newer Python versions
pattern.text._read = _read
##### MONKEY PATCH OF PATTERN 3.6.0 #####

def inorder_traversal(token, removed=None):
  if(len(list(token.children)) == 0):
     return token.text
  s = ""
  if(len(list(token.lefts)) != 0):
    for child in token.lefts:
      if(child != removed):
        s = s + " " + inorder_traversal(child, removed)

  s = s + " " + token.text

  if(len(list(token.rights)) != 0):
    for child in token.rights:
      if(child != removed):
        s = s + " " + inorder_traversal(child, removed)
  return s

def inorder_traversal_2(token, removed):
  if(len(list(token.children)) == 0):
     return token.text
  s = ""
  if(len(list(token.lefts)) != 0):
    for child in token.lefts:
      if(child not in removed):
        s = s + " " + inorder_traversal_2(child, removed)
    
  s = s + " " + token.text

  if(len(list(token.rights)) != 0):
    for child in token.rights:
      if(child not in removed):
        s = s + " " + inorder_traversal_2(child, removed)
  return s

def inorder_traversal_3(token, removed):
  if(len(list(token.children)) == 0):
     return token.text
  s = ""
  if(len(list(token.lefts)) != 0):
    for child in token.lefts:
      if(child not in removed):
        s = s + " " + inorder_traversal_3(child, removed)
  if(token not in removed):
    s = s + " " + token.text

  if(len(list(token.rights)) != 0):
    for child in token.rights:
      if(child not in removed):
        s = s + " " + inorder_traversal_3(child, removed)
  return s

def left_subtree(token):
  if(len(list(token.lefts)) == 0):
     return token.text
  s = ""
  if(len(list(token.lefts)) != 0):
    for child in token.lefts:
      s = s + " " + inorder_traversal(child)
  s = s + " " + token.text
  return s

def left_subtree_2(token, removed=None):
  if(len(list(token.children)) == 0):
     return token.text
  s = ""
  if(len(list(token.lefts)) != 0):
    for child in token.lefts:
      if(child != removed):
        s = s + " " + inorder_traversal(child, removed)

  s = s + " " + token.text
  return s

def left_subtree_3(token, removed):
  if(len(list(token.children)) == 0):
     return token.text
  s = ""
  if(len(list(token.lefts)) != 0):
    for child in token.lefts:
      if(child not in removed):
        s = s + " " + inorder_traversal_3(child, removed)

  if(token not in removed):
    s = s + " " + token.text
  return s


def right_subtree_3(token, removed):
  if(len(list(token.children)) == 0):
     return token.text
  s = ""
  if(len(list(token.rights)) != 0):
    for child in token.rights:
      if(child not in removed):
        s = s + " " + inorder_traversal_3(child, removed)

  if(token not in removed):
    s = s + " " + token.text
  return s

def get_root(doc):
  root  = None
  for token in doc:
    if(token.dep_ == "ROOT"):
      root = token
      return root

def get_root_stanza(doc):
  root  = None
  for token in doc:
    if(token.dep_ == "root"):
      root = token
      return root

def get_tag(token, tag):
  for child in token.children:
    if(child.dep_ == tag):
      return child

def find_in_subtree(token, tag):
  if(token == None):
     return
  if(token.tag_ == tag):
     return token
  for child in token.subtree:
    if(child.dep_ == tag):
      return child

def find_in_children(token, tag):
  if(token == None):
     return
  if(token.tag_ == tag):
     return token
  for child in token.children:
    if(child.dep_ == tag):
      return child

def pos_in_subtree(token, tag):
  if(token == None):
     return False
  if(token.pos_ == tag):
     return True
  for child in token.subtree:
    if(child.pos_ == tag):
      return True
  return False

def auxiliary_verb(verb, subj):
  if subj.tag_ in ("NN", "NNP"):
    if verb.tag_ in ("VBP", "VBZ", "VB"):
      aux = "is "
    elif verb.tag_ in ("VBD", "VBG", "VBN"):
      aux = "was "
    else: 
      aux = "are "
  elif subj.tag_ in ("NNS", "NNPS"):
    if verb.tag_ in ("VBP", "VBZ", "VB"):
      aux = "are "
    elif verb.tag_ in ("VBD", "VBG", "VBN"):
      aux = "were "
    else:
      aux = "are "
  elif subj.tag_ in ("PRP") and subj.text.lower() == "they":
    if verb.tag_ in ("VBP", "VBZ", "VB") :
      aux = "are "
    elif verb.tag_ in ("VBD", "VBG", "VBN"):
      aux = "were "
  elif subj.tag_ in ("PRP"):
    if verb.tag_ in ("VBP", "VBZ", "VB"):
      aux = "is "
    elif verb.tag_ in ("VBD", "VBG", "VBN"):
      aux = "was "
  else:
      aux = "are "
  return aux

def remove_punct(s):
    s_list = list(s.split(" "))
    if(s_list[0] in ['?', '!', ',', ';', '.']):
        s_list[0] = ""
    for i in range(len(s_list)):
        if(len(s_list[i]) > 0 and (s_list[i][0] == "." or s_list[i][0] == ",")):
            s_list[i] = "."
    s = " ".join(c for c in s_list)
    fix_spaces = re.compile(r'\s*([?!.,]+(?:\s+[?!.,]+)*)\s*')
    s = fix_spaces.sub(lambda x: "{} ".format(x.group(1).replace(" ", "")), s)
    s = truecase.get_true_case(s)
    return s

# Share a global level nlp pipeline to avoid repeated instantiation
spacy_nlp = spacy.load("en_core_web_lg")

def appositive_simplification_2(comp_sent):
  # nlp = spacy.load("en_core_web_sm")
  doc = spacy_nlp(comp_sent)

  root = get_root(doc)
  subj = get_tag(root, "nsubj")

  apposcl = None

  apposcl = find_in_subtree(root, "appos")

  if(apposcl == None):
    apposcl = find_in_subtree(root, "amod")
    if(apposcl != None):
      if(apposcl.head.dep_ != "nsubj"):
        print("Appos: No simplification(no subject)")
        return False, comp_sent
    else:
      print("Appos: No simplification")
      return False, comp_sent

  appos_subj = apposcl.head
  
  appos_phrase = inorder_traversal(apposcl)
  aux_verb = str(auxiliary_verb(root, appos_subj))
  noun_phrase = left_subtree_2(appos_subj, apposcl)
  sentence1 = inorder_traversal(root, apposcl)
  sentence1 = ' '.join(sentence1.split(",")) 
  sentence1 = ' '.join(sentence1.split()) + "."

  sentence2 = noun_phrase + " " + aux_verb + appos_phrase
  sentence2 = ' '.join(sentence2.split(",")) 
  sentence2 = ' '.join(sentence2.split()) + "."

  sentence1 = remove_punct(sentence1)
  sentence2 = remove_punct(sentence2)

  print(sentence1)
  print(sentence2)
  return True, sentence1 + " " + sentence2

def rel_order(token):
  if(token.dep_ == "nsubj" or token.dep_ == "nsubjpass"):
    return True
  else:
    return False

def relative_clause_simplify(cmp_snt):
  # nlp = spacy.load("en_core_web_sm") 
  doc = spacy_nlp(cmp_snt)
  root = get_root(doc)
  relcl = None
  relcl = find_in_subtree(root, "relcl")
  if(relcl == None):
    relcl = find_in_subtree(root, "rcmod")

  if(relcl == None):
    print("Relcl: No simplification")
    return False, cmp_snt

  subj = relcl.head

  rel_phrase = doc[relcl.left_edge.i : relcl.right_edge.i+1].text
  noun_phrase = left_subtree_2(subj, relcl)
  sentence1 = inorder_traversal(root, relcl)
  sentence1 = ' '.join(sentence1.split(",")) 
  sentence1 = ' '.join(sentence1.split()) + "."
  sentence2 = noun_phrase + " " + rel_phrase
  sentence2 = ' '.join(sentence2.split(",")) 
  sentence2 = ' '.join(sentence2.split()) 
  sentence2 = ' '.join(sentence2.split()) + "."
    
  sent1_doc = spacy_nlp(sentence1)
  sent1_root = get_root(sent1_doc)
  if(sent1_root.pos_ != "VERB" and sent1_root.pos_ != "AUX"):
    print("Relcl: No simplification")
    return False, cmp_snt

  order = rel_order(subj)
    
  sentence1 = remove_punct(sentence1)
  sentence2 = remove_punct(sentence2)

  if(not order):
    print(sentence1)
    print(sentence2)
    return True, sentence1 + " " + sentence2
  else:
    print(sentence2)
    print(sentence1)
    return True, sentence2 + " " + sentence1
  
def conjoint_clause_simplification(cmp_snt,Qnlp):
  cmp_snt = cmp_snt.rstrip(" ,.")
  print('the input is ',cmp_snt)
  doc = Qnlp(cmp_snt)
  root = get_root_stanza(doc)

  clause_type = None
    
    
  clause_type = find_in_children(root, "conj")
  if(clause_type == None):
    clause_type = find_in_children(root, "advcl")
  if(clause_type == None):
    clause_type = find_in_children(root, "parataxis")
  if(clause_type == None):
      clause_type = find_in_subtree(root, "conj")
  if(clause_type == None):
    clause_type = find_in_subtree(root, "advcl")
  if(clause_type == None):
    clause_type = find_in_subtree(root, "parataxis")
  if(clause_type == None):
    print("Conjoint: No simplification(no second clause found)")
    return False, cmp_snt

  clause_root = None

  if(clause_type.dep_ == "conj"):
    clause_root = find_in_subtree(root, "cc")
    if(clause_root != None):
      if((not pos_in_subtree(root, "VERB")) or (not (pos_in_subtree(clause_type, "VERB") or pos_in_subtree(clause_type, "AUX")))):
        print("Conjoint: No simplification 2(no verb in second clause)")
        return False, cmp_snt
    else:
      clause_root = find_in_children(clause_type, "advmod")
  elif(clause_type.dep_ == "advcl"):
    print("advcl")
    clause_root = find_in_children(clause_type, "mark")
    if(clause_root == None):
      clause_root = find_in_subtree(root, "mark")
    if(clause_root == None):
      clause_root = find_in_children(clause_type, "advmod")
    if(clause_root != None):
        if(clause_root.text == "to"):
            print("Conjoint: No simplification 3(no conjunction found)")
            return False, cmp_snt
  elif(clause_type.dep_ == "parataxis"):
    print("parataxis")
    clause_root = find_in_children(clause_type, "advmod")
  else:
    print("Conjoint: No simplification 3(no conjunction found)")
    return False, cmp_snt
  

  if(clause_root == None):
    print("Conjoint: No simplification 4")
    return False, cmp_snt
  
  clause_subj = None

  clause_subj = find_in_children(clause_type, "nsubj")
  if(clause_subj == None):
    clause_subj = find_in_children(clause_type, "nsubj:pass")
  clause_subj_flag = False
  if(clause_subj == None):
    clause_subj_flag = True
    clause_subj = find_in_children(root, "nsubj")
    if(clause_subj == None):
        clause_subj = find_in_children(root, "nsubj:pass")
    if(clause_subj == None):
        print("Conjoint: No simplification(no clause subject found)")
        return False, cmp_snt
    aux_str = ""
    for child in root.children:
        if(child.dep_ == "aux"):
            aux_str += child.text + " "
  modal = None
  if(clause_root.text.lower() in ['when', 'after', 'since', 'before', 'once']):
    modal = find_in_subtree(root, "aux")

  marker1 = ""
  marker2 = ""
  if(clause_root.text.lower() == "if"):
    marker1 = "Then"
    for child in root.subtree:
      if(child.text.lower() == "then"):
        marker1 = ""

  sentence1 = inorder_traversal_2(root, [clause_type, clause_root])
  
  sentence2 = ""
  marker2 = add_marker(clause_type, clause_root, modal) + " "
  if(clause_subj_flag):
    sentence2 = clause_subj.text + " " + aux_str + inorder_traversal(clause_type, clause_root)
  else:
    sentence2 = inorder_traversal(clause_type, clause_root)

  reverse = None

  if((root.i > clause_type.i) or (clause_root.text.lower() in ["because", "as"] and clause_root.i > 0)):
    if(clause_root.text.lower() in ['when', 'after', 'since', 'before', 'once'] and clause_root.i == 0):
      reverse = False
    else:
      reverse = True
  else:
    reverse = False
    
    
  if(clause_root.text.lower() in ["because", "as"] and clause_root.i > 0):
    sentence1 = marker2 + sentence1
    sentence2 = marker1 + sentence2
  else:
    sentence1 = marker1 + sentence1
    sentence2 = marker2 + sentence2
    
  s1 = remove_punct(sentence1)
  s2 = remove_punct(sentence2)
  exception_list = ["This happened", "This happens", "This was", "This is"]
  for c in ['when', 'after', 'since', 'before', 'once']:
        exception_list.append("This is " + c)
        exception_list.append("This was " + c)
        exception_list.append("This happens " + c)
        exception_list.append("This happened " + c)
        if(modal != None):
             exception_list.append('This ' + modal.text + ' happen ' + c)
  if(s1 in exception_list or s2 in exception_list):
        return False, cmp_snt
    
  if(reverse):
    print(sentence2)
    print(sentence1)
    return True, sentence2 + ". " + sentence1 + "."
  else:
    print(sentence1)
    print(sentence2)
    return True, sentence1 + ". " + sentence2 + "."

def add_marker(root, conj,  modal=None):
  conj_text = conj.text.lower()
  if(conj_text in ["and", "moreover"]):
    return "And"
  elif(conj_text == "if"):
    return "Suppose"
  elif(conj_text in ['though', 'although', 'but', 'whereas', 'however']):
    return "But"
  elif(conj_text in ['when', 'after', 'since', 'before', 'once']):
    if(conj.i > 0):
      if root.tag_ == 'VBP' or root.tag_ == 'VBZ' or root.tag_ == 'VB':
        return 'This is ' + conj_text + " "
      else:
        return 'This was ' + conj_text + " "
    else:
      if root.tag_ == 'VBP' or root.tag_ == 'VBZ':
        return 'This happens ' + conj_text + " "
      elif root.tag_ == 'VB' and modal != None: 
        return 'This ' + modal.text + ' happen ' + conj_text + " "
      else:
        return 'This happened ' + conj_text + " "
  elif conj_text in ['because', 'so', 'while', "therefore"]:
    return 'So '
  elif conj_text in ["nevertheless", "nonetheless", "yet"]:
    return 'But'
  elif conj_text == "otherwise":
    return 'or'
  elif conj_text == "unless":
    return 'unless'
  else:
     return ""
  
def change_verb_form(verb, v_aux, auxpass, subj_tag, subj_word):
    word_list = v_aux.split()
    new_verb = ""
    modal_list = ["can", "could", "must", "should", "will", "would", "may", "might", "shall"]
    if ('will' in word_list or 'would' in word_list) and auxpass != "been":
      print("future simple")
      new_verb = v_aux + conjugate(verb, 'pl')
    elif auxpass == 'been':
      if 'will' in word_list or 'would' in word_list:
        print("future perfect")
        new_verb = v_aux + verb
      elif 'has' in word_list or 'have' in word_list:
        print("present perfect")
        if bool(set(word_list) & set(modal_list)):
            new_verb = v_aux + verb
        elif subj_tag in ("NNS", "NNPS") :
            new_verb = "have " + verb
        elif subj_tag in ("NN", "NNP"):
            new_verb = "has " + verb
        elif subj_tag in ("PRP") and subj_word.lower() in ("them", "me", "you"):
            new_verb = "have " + verb
        elif subj_tag in ("PRP") and subj_word.lower() in ("it", "her", "him"):
            new_verb = "has " + verb
        else:
            new_verb = v_aux + verb
      elif 'had' in word_list:
        print("past perfect")
        new_verb = v_aux + verb
    elif auxpass == "being":
      if('was' in word_list or 'were' in word_list):
        print("past continous")
        if subj_tag in ("NNS", "NNPS"):
            new_verb = "were " + conjugate(verb, tense='present', aspect='progressive') 
        elif subj_tag in ("NN", "NNP"):
            new_verb = "was " + conjugate(verb, tense='present', aspect='progressive') 
        elif subj_tag in ("PRP") and subj_word.lower() in ("them", "you"):
            new_verb = "were " + conjugate(verb, tense='present', aspect='progressive')
        elif subj_tag in ("PRP") and subj_word.lower() in ("me", "it", "her", "him"):
            new_verb = "was " + conjugate(verb, tense='present', aspect='progressive')
        else:
            new_verb = "was " + conjugate(verb, tense='present', aspect='progressive')
      else:
        print("present continous")
        if subj_tag in ("NNS", "NNPS"):
            new_verb = "are " + conjugate(verb, tense='present', aspect='progressive') 
        elif subj_tag in ("NN", "NNP"):
            new_verb = "is " + conjugate(verb, tense='present', aspect='progressive') 
        elif subj_tag in ("PRP") and subj_word.lower() in ("them", "you"):
            new_verb = "are " + conjugate(verb, tense='present', aspect='progressive')
        elif subj_tag in ("PRP") and subj_word.lower() in ("it", "her", "him"):
            new_verb = "is " + conjugate(verb, tense='present', aspect='progressive')
        elif subj_tag in ("PRP") and subj_word.lower() in ("me"):
            new_verb = "am " + conjugate(verb, tense='present', aspect='progressive')
        else:
            new_verb = "is " + conjugate(verb, tense='present', aspect='progressive')
    elif auxpass in ['was', 'were']:
      print("simple past")
      if subj_tag in ("NNS", "NNPS"):
        new_verb = conjugate(verb, 'ppl') + " "
      elif subj_tag in ("NN", "NNP"):
        new_verb = conjugate(verb, '3sgp') + " "
      elif subj_tag in ("PRP") and subj_word.lower() in ("them", "me", "you"):
        new_verb = conjugate(verb, 'ppl') + " "
      elif subj_tag in ("PRP") and subj_word.lower() in ("it", "her", "him"):
        new_verb = conjugate(verb, '3sgp') + " "
      else:
        new_verb = conjugate(verb, '3sgp') + " "
    else:
      print("simple present")
      if subj_tag in ("NNS", "NNPS"):
        new_verb = conjugate(verb, 'pl') + " "
      elif subj_tag in ("NN", "NNP"):
        new_verb = conjugate(verb, '3sg') + " "
      elif subj_tag in ("PRP") and subj_word.lower() in ("them", "me", "you"):
        new_verb = conjugate(verb, 'pl') + " "
      elif subj_tag in ("PRP") and subj_word.lower() in ("it", "her", "him"):
        new_verb = conjugate(verb, '3sg') + " "
      else:
        new_verb = conjugate(verb, '3sg') + " "

    return new_verb

def change_pronoun_object(word):
  pron_list = {'me':'I', 'you':'you', 'him':'he', 'her':'she', 'it':'it', 'them':'they', 'us':'we'}
  word_list = word.split()
  for i in range(len(word_list)):
    if(word_list[i] in pron_list.keys()):
        word_list[i] = pron_list[word_list[i]]
  return " ".join(str(e) for e in word_list)

def change_pronoun_subject(word):
  pron_list = {'i':'me', 'you':'you', 'he': 'him', 'she':'her', 'it':'it', 'they':'them', 'we':'us'}
  word_list = word.split()
  word_list = word.split()
  for i in range(len(word_list)):
    if(word_list[i].lower() in pron_list.keys()):
        word_list[i] = pron_list[word_list[i].lower()]
  return " ".join(str(e) for e in word_list)

def passive_simplify(cmp_snt):
    # nlp=spacy.load('en_core_web_sm')
    doc = spacy_nlp(cmp_snt)
    simplify_flag = False
    root = get_root(doc)
    auxpass = find_in_children(root, "auxpass")
    if(auxpass == None):
        print("No passive clause found")
        return simplify_flag, cmp_snt
    agent = find_in_children(root, "agent")
    if(agent == None):
        print("No agent found")
        return simplify_flag, cmp_snt
    subj = find_in_children(root, "nsubjpass")
    if(subj == None):
        print("No subject found")
        return simplify_flag, cmp_snt
    
    simplify_flag = True
    
    aux = find_in_children(root, "aux")
    
    aux_tense = auxpass.tag_
    if aux_tense == 'VB' and aux != None:
        aux_tense = aux.tag_
    elif aux_tense == 'VBN' and aux != None:
        if aux.text.lower() not in ("has", "have", "had"):
            aux_tense = 'MD'

    new_obj = inorder_traversal(subj)
    obj = find_in_children(agent, "pobj")
    new_subj = inorder_traversal(obj)
    removed_aux = []
    for child in root.children:
        if(child.dep_ == "aux"):
            removed_aux.append(child)
    
    left_of_subj = ""
    right_of_subj = ""
    left_of_obj = ""
    right_of_obj = ""
    
    flag = 0
    for child in root.lefts:
        if(child.dep_ == "nsubjpass"):
            flag = 1
            continue
        if(flag == 0 and child not in [root, subj, auxpass, agent] + removed_aux):
            left_of_subj += inorder_traversal(child) + " "
        elif(flag == 1 and child not in [root, subj, auxpass, agent] + removed_aux):
            right_of_subj += inorder_traversal(child) + " "
            
    flag = 0
    for child in root.rights:
        if(child.dep_ == "agent"):
            continue
        if(((child.dep_ == "prt" or child.dep_ == "prep") and (len(list(child.children)) == 0)) and child not in [root, subj, auxpass, agent] + removed_aux):
            left_of_obj += inorder_traversal(child) + " "
        elif(child not in [root, subj, auxpass, agent] + removed_aux): 
            right_of_obj += inorder_traversal(child) + " "
    
    v_aux = ""
    if(aux != None):
        v_aux = aux.text
    aux_str = ""
    for child in root.children:
        if(child.dep_ == "aux"):
            aux_str += child.text + " "
    new_verb = change_verb_form(root.text, aux_str, auxpass.text, obj.tag_, obj.text)
    new_subj = change_pronoun_object(new_subj)
    new_obj = change_pronoun_subject(new_obj)
    final_sent = left_of_subj + " " + new_subj + " " + right_of_subj + " " + new_verb + " " + left_of_obj + " " + new_obj + " " + right_of_obj
    final_sent = ' '.join(final_sent.split())   
    final_sent = truecase.get_true_case(final_sent)
    final_sent = remove_punct(final_sent)
    print(final_sent)
    return simplify_flag, final_sent

def simplify(snt,Qnlp):
    doc=Qnlp(snt)
    flag = False
    final_snt = ""
    for s in doc.sents:
        flag, simp_snt = appositive_simplification_2(s.text)
        if(flag == True):
            print(simp_snt)
            final_snt += (simplify(simp_snt,Qnlp) + " ")
            continue
        else:
            flag, simp_snt = conjoint_clause_simplification(s.text,Qnlp)
            if(flag == True):
                print(simp_snt)
                final_snt += (simplify(simp_snt,Qnlp) + " ")
                continue
            else:
                flag, simp_snt = relative_clause_simplify(s.text)
                if(flag == True):
                    final_snt += (simplify(simp_snt,Qnlp) + " ")
                    continue
                else:
                    flag, simp_snt = passive_simplify(s.text)
                    if(flag == True):
                        final_snt += (simplify(simp_snt,Qnlp) + " ")
                        continue
                    else:
                        final_snt += (simp_snt + " ")
    return final_snt


# Custom simplifier wrapper around the DEPSYM code
from nltk.tokenize import sent_tokenize
from typing import *
import os, contextlib # For silencing output. From https://stackoverflow.com/a/28321717
from ..utils import detokenize_for_output

class DEPSYMSimplifier(AbstractSimplifier):
   
    def __init__(self):
        # Will hold onto the Stanza NLP object
        # Reuse across simplifications because this is heavy to create
        self.Qnlp = None

    def simplify_documents(self, documents:Union[List[str], str]) -> Union[List[List[str]], List[List[Tuple[str,str]]]]:
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

        # Split a document to its individual sentences
        orig_sents = []
        for document in documents:             
            # Split document into sentences using NLTK
            doc_sents = sent_tokenize(document, language='english')
            orig_sents.append(doc_sents)

        # Initialize stanza if not yet initialized
        if self.Qnlp is None:
            self.Qnlp = spacy_stanza.load_pipeline("en")

        # Create simplified predictions
        simp_docs = []
        simp_sents = []
        # For each document
        for doc_idx, doc_sents in enumerate(orig_sents):
            print(f"Simplifying document {doc_idx+1}")
            simp_doc_sents = []
            # Output silencing from https://stackoverflow.com/a/28321717
            with open(os.devnull, 'w') as devnull:
                with contextlib.redirect_stdout(devnull):
                    # For each sentence in the document
                    for comp_sent in doc_sents:
                        # Simplify the sentences
                        sentence = simplify(comp_sent, self.Qnlp)
                        # Fix formatting
                        sentence = detokenize_for_output(sentence)
                        simp_doc_sents.append(sentence)
            # Collect the simplified sentences per doument
            simp_docs.append(' '.join(simp_doc_sents))
            simp_sents.append(simp_doc_sents)
            
        # Create complex-simple sentence pairs
        orig_simp_pairs = []
        # For each doc that was processed
        for doc_idx in range(len(documents)):
            # Get all the orig and simplified sentences
            doc_orig_sents = orig_sents[doc_idx]
            doc_simp_sents = simp_sents[doc_idx]
            # Store as pair
            orig_simp_pairs.append([ (doc_orig_sents[sent_idx], doc_simp_sents[sent_idx] ) 
                                    for sent_idx in range(len(doc_orig_sents)) ])

        return simp_docs, orig_simp_pairs

