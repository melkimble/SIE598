import itertools

import spacy
from nltk import Tree
from spacy.symbols import *


def token_format(token):
    return " ".join([token.tag_, token.dep_, token.orth_])

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(token_format(node),
                   [to_nltk_tree(child)
                    for child in node.children]
               )
    else:
        return token_format(node)


def find_roots(doc):
    list_roots = []
    for possible_subject in doc:
        if possible_subject.dep in (nsubj, nsubjpass,agent) and possible_subject.head.pos == VERB \
                and (possible_subject.head.dep != ccomp ):

            list_roots.append(possible_subject.head)

    return list_roots

def find_verbs(doc):
    list_verbs = []
    for possible_verb in doc:
        if possible_verb.dep != root and possible_verb.pos == VERB and possible_verb.dep != amod \
                and possible_verb.dep != ccomp:
            list_verbs.append(possible_verb)

    return list_verbs

def get_tag_by_word(doc,w):
     for word in doc:
        if w == word:
            return word.tag_

def get_dep_by_word(doc,w):
     for word in doc:
        if w == word:
            return word.dep_

def get_subtree_of(doc,w):
    for word in doc:
        if w == word:
            return word.subtree

def find_objects(doc,a):
    list_objects = []
    for possible_object in doc:
        print(possible_object,possible_object.pos_)
        if possible_object.dep in (dobj,pobj) and possible_object.head.pos in (VERB, ADP) and possible_object.head  in a  and possible_object.head.orth_ not in ('in','In'):
            list_objects.append([possible_object,possible_object.head])
    return list_objects


def find_subjects(doc):
    list_subject = []
    for possible_subject in doc:
        if possible_subject.dep in (nsubj,nsubjpass) and possible_subject.head.pos == VERB and possible_subject.pos in (PROPN, NOUN, PRON):
            list_subject.append([possible_subject,possible_subject.head])

    return list_subject

def find(doc,w):
    list_subject = []
    for p in doc:
        if p == w:
            return p.rights

def findLefts(doc,w):
    list_subject = []
    for p in doc:
        if p == w:
            return p.lefts

def remove_duplicates(triples_):
    try:
        return list(triples for triples,_ in itertools.groupby(triples_))
    except:
        return triples_


