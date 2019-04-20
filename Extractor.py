import csv
import json
import os
from collections import defaultdict
from itertools import chain
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

annotators = 'tokenize, ssplit, pos, ner, coref'
options = {'openie.resolve_coref': True}

nlp = StanfordCoreNLP(annotators=annotators, options=options)
sdp = CoreNLPDependencyParser()

#-----------------------------------------------------------------------------------------------------------------------
#LOAD THE SENTENCES
filepath = 'kolbuszowa.txt'
list_sentences = []
with open(filepath,encoding="utf8") as file:
     for line in file:
         list_sentences.append([line[:line.rfind(".") + 1]])

#PREPROCESSING START
#CREATE TEMPORARY LIST FOR ADJUCENT SENTECNES FOR COREFERENCING (PREVIOUS 2 SENTENCES)
for i in range(len(list_sentences)):
        adj_sentences = []
        start_index = i - 1
        if (start_index < 0):
                start_index = 0 - len(list_sentences)
        for item in list_sentences[start_index:i+1]:
                adj_sentences.append(item[0]+" ")


        #FINDINF COREFERENCES
        combined_sentences = ''.join(str(e) for e in adj_sentences)
        document = nlp(combined_sentences.encode('utf-8'))

        if(len(document.coref_chains)) > 0:
                chain = document.coref_chains[0]
                print(combined_sentences)
                print(chain)
                print('--------------------------------------------------------------------------------------------')

