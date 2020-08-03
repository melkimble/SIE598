import csv
import json
import os
from collections import defaultdict
from itertools import chain

import pynlp
from nltk.tag import StanfordNERTagger
import nltk
from nltk.corpus import wordnet as wn
from nltk.parse.corenlp import CoreNLPDependencyParser
from graphviz import Source
from pattern.vector import stemmer
from pycorenlp import StanfordCoreNLP
from sutime import SUTime
from textblob import TextBlob
from stanfordnlp.server import CoreNLPClient
from pynlp import StanfordCoreNLP
from pycorenlp import *

from Util import get_tree, get_left_children, get_children, get_wordnet_pos, get_right_children

synonyms = {'soldiers':'troopers', 'soldier':'trooper'}

annotators = 'pos, ner, depparse, openie'
options = {'openie.resolve_coref': True}

nlp_ = pynlp.StanfordCoreNLP(annotators=annotators, options=options)
nlp=StanfordCoreNLP("http://localhost:9000/")

sdp = CoreNLPDependencyParser()
jar_files = os.path.join(os.path.dirname(__file__), 'jars')
sutime = SUTime(jars=jar_files, mark_time_ranges=True, include_range=True)
lemmatizer = nltk.WordNetLemmatizer()
#-----------------------------------------------------------------------------------------------------------------------
#LOAD THE SENTENCES
filepath = 'kolbuszowa.txt'
list_sentences = []
with open(filepath,encoding="utf8") as file:
     for line in file:
         list_sentences.append([line[:line.rfind(".") + 1]])

#PREPROCESSING START
for i in range(len(list_sentences)):
    sentence = list_sentences[i][0]
    #PREPROCESSING
    jsn = json.dumps(sutime.parse(sentence), sort_keys=True, indent=4)
    d = json.loads(jsn)

    if (len(d) >0):
        sentence = sentence.replace(d[0]['text'], d[0]['value'])

    for key in synonyms.keys():
        sentence = sentence.replace(key,synonyms[key])


    #CREATE DEPENDANCY TREE
    result = list(sdp.raw_parse(sentence))
    tree = get_tree(result[0],4)
    dep_tree_dot_repr = tree.to_dot()
    #source = Source(dep_tree_dot_repr, filename="dep_tree", format="png")
    #source.view()

    #REMOVING UNNECESSARY PARTS (Upon bla bla, Following invasion bla bla, etc) ----------------------------------------
    sentence_parts={}

    root_vbd_address = tree.get_by_address(0)['deps']['ROOT'][0]
    root_vbd = tree.get_by_address(root_vbd_address)
    sentence_parts[root_vbd['rel']] =[root_vbd['word'],root_vbd_address, 0]

    left_children = get_left_children(tree,root_vbd_address)

    for child in left_children:
        sentence_parts[child['rel']]= [child['word'],child['address'], len(child['deps'])]

    right_children = get_right_children(tree,root_vbd_address)

    for child in right_children:
        sentence_parts[child['rel']]= [child['word'],child['address'],len(child['deps'])]
    print(sentence_parts)
    if 'case' in sentence_parts and 'nsubj' not in sentence_parts and 'nsubjpass' not in sentence_parts:
        word_addresses_to_remove =[]
        for key in sentence_parts.keys():

            if sentence_parts[key][2] >0 and key != 'punct':
                word_addresses_to_remove.append(tree.get_by_address(sentence_parts[key][1])['address'])
                [word_addresses_to_remove.append(child ['address']) for child in get_children(tree, tree.get_by_address(sentence_parts[key][1]))]
            else:
                word_addresses_to_remove.append(tree.get_by_address(sentence_parts[key][1])['address'])
        str_ =''
       # str_ = ' '.join([tree.get_by_address(address)['word'] for address in sorted(word_addresses_to_remove)])
        for address in sorted(word_addresses_to_remove):
            if tree.get_by_address(address)['word'] != ',':
                str_ += ' ' + tree.get_by_address(address)['word']
            else:
                str_ +=  tree.get_by_address(address)['word']
        sentence = sentence.replace(str_.strip(),'')


    #CREATE DEPENDANCY TREE AGAIN!
    result = list(sdp.raw_parse(sentence))
    tree = get_tree(result[0],4)
    dep_tree_dot_repr = tree.to_dot()
    #source = Source(dep_tree_dot_repr, filename="dep_tree", format="png")
    #source.view()


    #--------------------------------------------------------------------------------------------------------------------


    ROOTS = []

    #VALIDATING ROOT
    root = tree.get_by_address(0)
    VBD = tree.get_by_address(root['deps']['ROOT'][0])

    VBD_word = VBD['word']

    if (len(VBD['word'].split())>1):
        VBD_word= VBD['word'].split()[1]

    #IF THE VERB ROOT IS FOLLOWED BY A 'CASE' THEN THAT IS HIGHLY LIKLELY NOT THE ROOT. PROBABLY REMOVE THE TREE
    left_children = get_left_children(tree, VBD['address'])
    isValidRoot = True

    for child in left_children:
        if child['rel'] == 'case':
            isValidRoot = False

    all_children = get_children(tree,root)
    count_roots =0
    for child in all_children:
        if child['rel'].lower() == 'root':
            count_roots +=1
            ROOTS.append(child)

    #BUILD DEPENDENCY TREES FOR EACH ROOT
    trees ={}
    print(ROOTS)
    for root in ROOTS:
        all_children = get_children(tree,root)
        word_addresses = [root['address']]
        trees[root['word']]=[]

        for child in all_children:
            if child['rel'].lower() == 'root':
                break

            word_addresses.append(child['address'])

        trees[root['word']].append(sorted(word_addresses))

        #CREATE DEPENDANCY TREES FOR EACH NOW
        sentences = []

        for key in trees.keys():
            sent =''
            for address in trees[key][0]:

                if tree.get_by_address(address)['word']!=',' and tree.get_by_address(address)['word'] !='.':
                    sent += tree.get_by_address(address)['word'] + ' '
                    #print (sent)

            sentences.append([root['address'],sent])


    #VALIDATING SENTENCES
    i =0
    sentence_parts_collection = {}

    for sentence in sentences:

        possible_nouns= []
        sentence_parts = { }
        lem_sentence=sentence[1]
        print(lem_sentence)
        #lem_sentence = ' '.join([lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in nltk.word_tokenize(sentence[1])])

        #GET NAME ENTITIES --TO IDENTIFY THE SUBJECTS/OBJECTS
        document = nlp_(lem_sentence)
        [possible_nouns.append(str(entity)) for entity in document.entities if entity.type == 'MISC' or entity.type == 'PERSON' or entity.type == 'ORGANIZATION' or entity.type == 'LOCATION']


        #BUILD THE DEP TREE

        result = list(sdp.raw_parse(lem_sentence))
        tree = get_tree(result[0],4)
#        dep_tree_dot_repr = tree.to_dot()
        i +=1


        #OPTIONAL
       # source = Source(dep_tree_dot_repr, filename="dep_tree" + str(i), format="png")
       # source.view()


        #VALIDATE THE ROOTS AGAIN AS NOW THESE TREES ARE NEWLY GENERATED
        root_vbd_address = tree.get_by_address(0)['deps']['ROOT'][0]
        root_vbd = tree.get_by_address(root_vbd_address)
        sentence[0] = root_vbd_address
        sentence_parts[root_vbd['rel']] =[root_vbd['word'],root_vbd_address, 0]

        #CHECK SUBJECT / OBJECT AVILABILITY
        left_children = get_left_children(tree,root_vbd_address)

        for child in left_children:
            sentence_parts[child['rel']]= [child['word'],child['address'], len(child['deps'])]

        #CHECK SUBJECT / OBJECT AVILABILITY
        right_children = get_right_children(tree,root_vbd_address)

        for child in right_children:
            #CHECK FOR ACTIVE SUBJECT
            sentence_parts[child['rel']]= [child['word'],child['address'],len(child['deps'])]


        #ANALYZE THE SENTENCE PART
        if 'nsubj' in sentence_parts: #active voice = TRUE
            #CHECK IF THE SUBJECT IS AN ACTUAL SUBJECT BY COMAPRING WITH NERs
            if not sentence_parts['nsubj'][0] in possible_nouns:
                #TRAVERSE THE SUBTREE
                all_children = get_children(tree,tree.get_by_address( sentence_parts['nsubj'][1]))
                for child in all_children:
                    if child['word'] in possible_nouns:
                        sentence_parts['nsubj'][0] = child['word']
                        sentence_parts['nsubj'][1] = 0
                        sentence_parts['nsubj'][2] = 0
                        break

        if 'nsubjpass' in sentence_parts: #active voice = FALSE
            #CHECK IF THE SUBJECT IS AN ACTUAL SUBJECT BY COMAPRING WITH NERs
            if not sentence_parts['nsubjpass'][0] in possible_nouns:
                #TRAVERSE THE SUBTREE
                all_children = get_children(tree,tree.get_by_address( sentence_parts['nsubjpass'][1]))
                for child in all_children:
                    if child['word'] in possible_nouns:
                        sentence_parts['nsubjpass'][0] = child['word']
                        sentence_parts['nsubjpass'][1] = 0
                        sentence_parts['nsubjpass'][2] = 0
                        break

            #CORRECT THE ROOT IF IT IS PASSIVE
            previous_to_root_node = tree.get_by_address(sentence_parts['ROOT'][1] - 1)
            if 'auxpass' in previous_to_root_node['rel'] :
                sentence_parts['ROOT'][0]= tree.get_by_address(sentence_parts['ROOT'][1] - 1)['word'] + sentence_parts['ROOT'][0].capitalize()

        #CHECK IF CONJUNCTIONS; IF SO, THERE SHOULD BE ANOTHER NOUN PHRASE
        for child in get_children(tree,root_vbd):
            extra_noun_phrase =[]
            if child['rel'] == 'conj':
                extra_noun_phrase.append(child['address'])
                [extra_noun_phrase.append(child['address']) for child in get_children(tree,tree.get_by_address(child['address']))]
                str_ = ''
                str_ = ' '.join([ tree.get_by_address(address)['word'] for address in sorted(extra_noun_phrase)])


                if 'nsubj' in sentence_parts:
                    if 'aux' in sentence_parts:
                        sentences.append([0,sentence_parts['aux'][0]+' ' + sentence_parts['nsubj'][0]+' ' + str_,])
                    else:
                        sentences.append([0,sentence_parts['nsubj'][0]+' ' + str_,])

                if 'nsubjpass' in sentence_parts:
                    sentences.append([0,sentence_parts['nsubjpass'][0]+' '+sentence_parts['auxpass'][0]+' ' + str_,])

        sentence_parts_collection[lem_sentence] =  sentence_parts

    #FURTHER REFINEMENT
    LOCAL_TRIPLES = {}
    METADATA = []
    sentence_parts_collection_v2 = {}
    for key in sentence_parts_collection.keys():
        triple = {}

        #GENERATE DEP TREE AGAIN!
        result = list(sdp.raw_parse(key))
        tree = get_tree(result[0],4)

        sentence_parts = sentence_parts_collection[key]

        if 'case'  in sentence_parts and 'nsubj' not in sentence_parts and 'nsubjpass' not in sentence_parts:
            METADATA.append(key)
        else:
            sentence_parts_collection_v2[key] = sentence_parts_collection[key]

    for key in sentence_parts_collection_v2.keys():
        triple = {}

        #GENERATE DEP TREE AGAIN!
        result = list(sdp.raw_parse(key))
        tree = get_tree(result[0],4)

        sentence_parts = sentence_parts_collection_v2[key]

        list_nodes = []
        object_str =''
        if 'conj' in sentence_parts: #SHOULD HAVE ANOTHER SENTENCE AFTER THIS ONE
            if not 'dobj' in sentence_parts and not 'nobj' in sentence_parts and not 'nobjpass' in sentence_parts: #NO OBJECT FOUND
                #GENERATE OBJECT
                all_children = get_children(tree, tree.get_by_address(sentence_parts['conj'][1]))
                [list_nodes.append(child['address']) for child in all_children]

                #CONSTUCT OBJECT
                object_str =' '.join( tree.get_by_address(node)['word'] for node in sorted(list_nodes))



        if 'nsubj' in sentence_parts:
            triple['SUBJECT'] = sentence_parts['nsubj'][0]
        if 'nsubjpass' in sentence_parts:
            triple['SUBJECT'] = sentence_parts['nsubjpass'][0]

        triple['PREDICATE'] = sentence_parts['ROOT'][0]
        triple['OBJECT'] = object_str


        triple['META'] = METADATA

        print (triple)

    #break #DEBUG
