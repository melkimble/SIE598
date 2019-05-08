import sys
from datetime import datetime, timedelta
from itertools import chain
import re
import nltk
from dateutil import parser
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
    #print(a)
    list_objects = []
    for possible_object in doc:
        #print(possible_object,possible_object.pos_,possible_object)
        if possible_object.dep == (pobj) and possible_object.head.pos == ADP  and possible_object.head.head  in a and possible_object.orth_ not in ('time','Time') and possible_object.head.orth_ not in ('After','Before'):
            list_objects.append([possible_object,possible_object.head.head])
        if possible_object.dep == (dobj) and possible_object.head.pos == VERB and possible_object.head.dep_ in ('ccomp','xcomp') and possible_object.head.head  in a and possible_object.orth_ not in ('time','Time'):
            list_objects.append([possible_object,possible_object.head.head])
        if possible_object.dep == (dobj) and possible_object.head.pos == VERB and possible_object.head.dep_ in ('xcomp') and possible_object.head.head  in a and possible_object.orth_ not in ('time','Time'):
            list_objects.append([possible_object,possible_object.head])
        if possible_object.dep == (dobj) and possible_object.head.pos == VERB  and possible_object.head  in a  and possible_object.head.orth_ not in ('in','In'):
            list_objects.append([possible_object,possible_object.head])
        if possible_object.dep == (dobj) and possible_object.head.pos == VERB and possible_object.head.head.pos == VERB and possible_object.head.head.dep_ != 'xcomp' and possible_object.head.dep_ != 'advcl'  \
                and possible_object.head  in a  and possible_object.head.orth_ not in ('in','In'):
            if list(possible_object.head.head.rights)[0].dep_ != 'dobj':
                list_objects.append([possible_object,possible_object.head.head])


    #cleanup objects

    for obj in list_objects:
        closest_obj =None
        verb = obj[1]
        for word in list(verb.rights):
            for inner_word in list(word.rights):
                if closest_obj == None:
                    if inner_word.dep_ == 'pobj':
                        closest_obj = inner_word
                        break

        #for obj_ in list_objects:
            #if obj_[0] != None and obj_[1] == verb and obj_[0] != obj[0] and obj_[0].dep_ == 'pobj':
                #get closest pobj to the verb
                #if closest_obj != obj_[0]:
                    #obj_[0] = None


    for obj in list_objects:
        closest_obj =None
        verb = obj[1]
        for word in list(verb.rights):

            if closest_obj == None:
                if word.dep_ == 'dobj':
                    closest_obj = word
                    break


        for obj_ in list_objects:
            if obj_[0] != None  and closest_obj != None and obj_[1] == verb and obj_[0] != obj[0] and obj_[0].dep_ != 'dobj':
                #get closest pobj to the verb
                if closest_obj != obj_[0]:
                    obj_[0] = None


        for obj in list_objects:
            closest_obj =None
            verb = obj[1]
            for word in list(verb.rights):

                if closest_obj == None:
                    if word.dep_ == 'pobj':
                        closest_obj = word
                        break


            for obj_ in list_objects:
                if obj_[0] != None  and closest_obj != None and obj_[1] == verb and obj_[0] != obj[0] and obj_[0].dep_ != 'pobj':
                    #get closest pobj to the verb
                    if closest_obj != obj_[0]:
                        obj_[0] = None

    for obj in list_objects:
        if obj[0] == None or obj[0].dep_ == 'npadvmod':

            list_objects.remove(obj)



    return list_objects


def find_subjects(doc):
    list_subject = []
    for possible_subject in doc:
        #print(possible_subject,possible_subject.dep_,possible_subject.pos_)
        if possible_subject.dep in (nsubj,nsubjpass) and possible_subject.head.pos == VERB and possible_subject.pos in (PROPN, NOUN, PRON, ADV,X):
            list_subject.append([possible_subject,possible_subject.head])

    return list_subject

def find(doc,w):
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
        print (sys.exc_info())
        return triples_

def form_triples(triples_):

    triples_new = []
    for item in triples_:
        i=0
        S=' '
        P=' '
        O=' '
        M=' '
        D=' '

        for inner_item in item: #SPO
            i+=1
            if inner_item != None:
                for inner_inner_item in inner_item:
                    if inner_inner_item != None and type(inner_inner_item) == list:
                        for inner_inner_inner_item in inner_inner_item:
                            if i==1:
                                S +=' ' + str(inner_inner_inner_item)
                            if i==2:
                                P +=' ' +  str(inner_inner_inner_item)
                            if i==3:
                                O +=' ' +  str(inner_inner_inner_item)
                            if i==4:
                                O +=' ' +  str(inner_inner_inner_item)
                            if i==5:
                                D +=' ' +  str(inner_inner_inner_item)
                    else:
                        if i==1:
                                S +=' ' +  str(inner_inner_item)
                        if i==2:
                                P +=' ' +  str(inner_inner_item)
                        if i==3:
                                O +=' ' +  str(inner_inner_item)
                        if i==4:
                                M += str(inner_inner_item)
                        if i==5:
                                D += str(inner_inner_item)

        triple_new = [re.sub(' +', ' ', S),re.sub(' +', ' ', P),re.sub(' +', ' ', O),re.sub(' +', ' ', M),re.sub(' +', ' ', D)]

        triples_new.append(triple_new)


    return [a for i, a in enumerate(triples_new) if not any(all(c in h for c in a) for h in triples_new[:i])]

def build_object(obj):
    children=[]
    try:
        if(len(list(obj.lefts))>0 and not (len(list(obj.lefts))==1 and list(obj.lefts)[0].pos in (DET,CCONJ) )):
            children = list(obj.lefts)
            children.append(obj)
        elif (len(list(obj.rights))>0):
            if len([word for word in list(obj.subtree) if word.orth_ in ('in','In')])==0:
                [children .append(word) for word in list(obj.subtree)]
            elif len([word for word in list(obj.subtree) if word.pos != VERB])==0:
                children.append(obj)
                [children .append(word) for word in list(obj.rights)]
            else:
                children.append(obj)
        else:
            children.append(obj)



    except :
        children.append(obj)

    for child in children:
        if type(child) != type(object) and child != None and child.pos in (DET,CCONJ):
            children.remove(child)

   # print(children)
    return children

def build_metadata(obj):

    children=[]
    try:
        if (len(list(obj.subtree))>0):

            if obj.head.dep_ not in ('conj','advcl'):
                ([children.append(word) for word in list(obj.subtree)])

            else:
                [children.append(word) for word in list(obj.head.subtree) ]
    except :
        children.append(None)

    for child in children:
        if type(child) != type(object) and child != None  and child.pos  in (DET,PUNCT) :

            children.remove(child)

    if len(children) == 1:
        children=[None]

    return ' '.join([child.orth_ for child in children if child != None])

def build_subject(subj):
    children=[]

    try:
        if(len(list(subj.lefts))>0):
            children = list(subj.lefts)
        elif (len(list(subj.rights))>0):
            children = list(subj.rights)

        children.append(subj)
    except :
        children.append(subj)

    for child in children:
        if type(child) != type(object) and child != None and child.pos in (DET,CCONJ):
            children.remove(child)

   # print(children)
    return children

def last_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - timedelta(days=1)

def cleanup(date):
    try:
        yield parser.parse(date, dayfirst=False)
    except (ValueError, TypeError) as e:
        print('')
        #print("Exception {} on unhandled date {}".format(e, date))


