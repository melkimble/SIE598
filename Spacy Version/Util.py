from itertools import chain

import nltk
from nltk.corpus import wordnet as wn

def count_children(tree,node_index):
        children = chain.from_iterable(tree.nodes[node_index]['deps'].values())
        index = tree.nodes[node_index]['address']

        return sum(1 for c in children if c < index or c > index)

def get_tree(tree,node_index):
        children = chain.from_iterable(tree.nodes[node_index]['deps'].values())
        index = tree.nodes[node_index]['address']
        for c in children:
            if c < index:
                wn_list = wn.synsets(tree.get_by_address(c)['word'])

                if (len ( wn_list)>0 and index - c == 1 and  wn_list[0].pos() =="v" ):
                    tree.get_by_address(index)['word'] = tree.get_by_address(c)['word'] + " " + tree.get_by_address(index)['word']
                    #tree.remove_by_address(c)
                    #print (tree.get_by_address(c))
        return tree
        #return sum(1 for c in children if c < index)

def get_left_children(tree,node_index):
        children = chain.from_iterable(tree.nodes[node_index]['deps'].values())
        index = tree.nodes[node_index]['address']
        l_children = []
        for c in children:
            if c < index:
                l_children.append(tree.get_by_address(c))
        return l_children

def get_right_children(tree,node_index):
        children = chain.from_iterable(tree.nodes[node_index]['deps'].values())
        index = tree.nodes[node_index]['address']
        r_children = []
        for c in children:
            if c > index:
                r_children.append(tree.get_by_address(c))
        return r_children

def get_children(tree, node):
        for childs in node['deps'].values():
            for child in childs:
                yield tree.get_by_address(child)
                for grandchild in get_children(tree,tree.get_by_address(child)):
                    yield grandchild

def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wn.ADJ,
                "N": wn.NOUN,
                "V": wn.VERB,
                "R": wn.ADV}

    return tag_dict.get(tag, wn.NOUN)


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
        if possible_subject.dep in (nsubj, nsubjpass,agent,aux) and possible_subject.head.pos == VERB \
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
        if possible_object.dep in (dobj,pobj) and possible_object.head.pos in (VERB, ADP) and possible_object.head  in a  and possible_object.head.orth_ not in ('in','In'):
            list_objects.append([possible_object,possible_object.head])
    return list_objects


def find_subjects(doc):
    list_subject = []
    for possible_subject in doc:
        if possible_subject.dep in (nsubj,nsubjpass) and possible_subject.head.pos == VERB and possible_subject.pos in (PROPN, NOUN, PRON, ADV):
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


