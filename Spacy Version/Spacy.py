import itertools
from copy import copy

import spacy
from nltk import Tree
from Util import to_nltk_tree, find_roots, get_tag_by_word, get_dep_by_word, get_subtree_of, find_objects, find_verbs, \
    find_subjects, find, findLefts, remove_duplicates
import re

nlp = spacy.load('en_core_web_sm')

#------------BEGIN-------------------------------
sent = 'Kolbuszowa is located about 150 kilometers (94 miles) east of Kraków. '

#Remove paranthesis and words in it
regex = re.compile("[\(\[].*?[\)\]]")
result = re.findall(regex, sent)

omit_words = ['were']

for word in result:
    omit_words.append(word)


doc1 = nlp(sent)
temp_roots = find_roots(doc1)

#Check if it has one root and it is in the omit words. If so, dont remove
if len(temp_roots)== 1 and len([w for w in list(temp_roots[0].lefts) if w.dep_ == 'aux'])==0:
    for word in omit_words:
        sent = sent.replace(word,'')

sent  = re.sub(' +', ' ', sent)


doc1 = nlp(sent)

omit_verbs = ['was','had','did']

print(sent)

#FIND ROOTS
list_roots = find_roots(doc1)
list_verbs = find_verbs(doc1)



for verb in list_verbs:
    for omit_verb in omit_verbs:
        if verb.orth_ == omit_verb:
            list_verbs.remove(verb)

list_objects = find_objects(doc1, list_verbs)
list_subjects = find_subjects(doc1)

print('ROOTS',list_roots)
print('OBJECTS',list_objects)
print('SUBJECTS',list_subjects)
print('VERBS',list_verbs)
print('ROOTS',list_roots)



#Make Structure
for root in list_roots:
    triples = []
    subject = ''


    for item in list_subjects:
        if item[1] == root:
            subject = item[0]


    for item in list_objects:
        if item[1] == root:
            object = item[0]

    #PREDICATES
    for verb in list_verbs:

        if len(list_roots) == 1 and  (verb.dep_ != verb.head.dep_ or verb == verb.head)\
                or (len(list_roots) > 1 and  verb.dep_ != verb.head.dep_ ):

            for child_word in list(find(doc1,verb)):
                #object = ''
                for item in list_objects:
                    if item[1] == child_word:
                        object = item[0]



                if get_dep_by_word(doc1,verb) in ('xcomp'):
                    if get_dep_by_word(doc1,child_word) == 'xcomp' or get_dep_by_word(doc1,child_word) == 'conj' :

                        for item in list_objects:
                            if item[1] == child_word:
                                object = item[0]

                        triples.append([[subject], [str(root) + ' ' +  str(child_word)], [object]])


                        for item in list_objects:
                            if item[1] == verb:
                                object = item[0]

                        triples.append([[subject], [str(root) + ' ' +  str(verb)], [object]])

                else:

                    if get_dep_by_word(doc1,child_word) == 'conj' and child_word.head.dep_ != 'conj':
                        for item in list_objects:
                            if item[1] == root:
                                object = item[0]

                        triples.append([[subject], [str(root)], [object]])
                        for item in list_objects:
                            if item[1] == child_word:
                                object = item[0]
                        triples.append([[subject], [str(child_word)], [object]])
                    else:
                        if len(list(find(doc1,root)))>0:
                            #-----------------------------------RIGHT----------------------
                            for word in find(doc1,list(find(doc1,root))[0]):
                                if word.dep_ == 'pobj':
                                    object = word
                                    break

                            if list(find(doc1,root))[0].dep_ in ('prep','agent'):
                                triples.append([[subject], [str(root) +' ' + str(list(find(doc1,root))[0])], [object]])
                            else:
                                for obj in list_objects:
                                    if obj[1] == root and obj[0].orth_ == object.orth_:
                                        triples.append([[subject], [str(root)], [object]])
                            #-----------------------------------LEFT----------------------
                            if len(list(findLefts(doc1,root)))>0:

                                for word in find(doc1,list(find(doc1,root))[0]):
                                    if word.dep_ == 'pobj':
                                        object = word
                                        break
                                if len(triples) == 0:
                                    if list(findLefts(doc1,root))[0].dep_ in ('prep','agent'):
                                        triples.append([[subject], [str(root) +' ' + str(list(findLefts(doc1,root))[0])], [object]])
                                    else:
                                        for obj in list_objects:
                                            if obj[1] == root and obj[0].orth_ == object:
                                                triples.append([[subject], [str(root)], [object]])

                        elif len(list(findLefts(doc1,root)))>0:

                            for word in findLefts(doc1,list(findLefts(doc1,root))[0]):
                                if word.dep_ == 'pobj':
                                    object = word
                                    break

                            if list(findLefts(doc1,root))[0].dep_ in ('prep','agent'):
                                triples.append([[subject], [str(root) +' ' + str(list(findLefts(doc1,root))[0])], [object]])
                            else:
                                for obj in list_objects:
                                    if obj[1] == root and obj[0].orth_ == object .orth_:
                                        triples.append([[subject], [str(root)], [object]])




                    if get_dep_by_word(doc1,child_word) == 'advmod' and list(find(doc1,verb))[0] == child_word:

                        if (len(list(find(doc1,child_word))))>0:
                            if get_dep_by_word(doc1,list(find(doc1,child_word))[0] )  == 'prep':
                                #Find Object if any

                                for word in find(doc1,list(find(doc1,child_word))[0]):
                                    if word.dep_ == 'pobj':
                                        object = word
                                        break

                                triples.append([[subject], [str(root) + ' ' +  str(child_word) + ' ' + str(list(find(doc1,child_word))[0]) ], [object]])


                    if get_dep_by_word(doc1,child_word) == 'prep' and  child_word.orth_ not in ('On', 'on','of'):
                        for word in list(find(doc1,child_word)):
                            if word.dep_ == 'pobj':
                                object = word
                                break

                        for obj in list_objects:
                            if obj[1] == root and obj[0].orth_ == object.orth_:
                                triples.append([[subject], [str(root) + ' ' +  str(child_word)  ], [object]])


    print(remove_duplicates(triples))


[to_nltk_tree(sent.root).pretty_print() for sent in doc1.sents]
