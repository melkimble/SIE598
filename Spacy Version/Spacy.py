import itertools
from copy import copy

import spacy
from nltk import Tree
from spacy.symbols import VERB, NOUN, PRON

from Util import to_nltk_tree, find_roots, get_tag_by_word, get_dep_by_word, get_subtree_of, find_objects, find_verbs, \
    find_subjects, find, findLefts, remove_duplicates, build_object, build_subject, build_metadata, form_triples
import re

nlp = spacy.load('en_core_web_sm')

#------------BEGIN-------------------------------
sentences = ['Some Kolbuszowa Jews were sent from Rzeszów to the Jasionka labor camp, where most were murdered or died of starvation.  ',
             'The Jews were registered and performed forced labor in rotation.  ',
             'Upon capture of the town, about two weeks later, German soldiers began kidnapping Jews for forced labor, and searching Jewish homes for valuables.',
             'That night they surrounded the ghetto and arrested 26 Jews, including most of the Judenrat.',
             'Kolbuszowa is located about 150 kilometers (94 miles) east of Kraków. ',
             'On the outbreak of World War II, around 2,500 Jews were residing in the town.',
             'Following the German invasion on September 1, 1939, many Jewish refugees arrived in Kolbuszowa. ',
             'At this time, many Jewish homes were burned down and looted.',
             'So a Jewish council (Judenrat) was established in March 1940, headed by Dr. Leon Anderman. ',
             'In June 1941, Landkommissar Twardon arrived in Kolbuszowa.',
             'In July 1940, all Jews aged 12 through 60 were registered and issued work cards. ',
             'In November another roundup occurred; this time 80 Jews were chosen for forced labor in Pustków.',
             'On June 13, Twardon gave the Jews only 48 hours to move into the ghetto, which was located in the poorest section of town, where 700 Jews and 90 Poles resided. ',
             'The arrested Jews were sent to Auschwitz. ',
             'The Judenrat established a public kitchen, where many Jews received their only meal of the day. ',
             'On June 28, 1942, Twardon went to Rzeszów and ordered a group of Jewish men to return to Kolbuszowa to dismantle the ghetto houses. ',
             'The men were housed in the Bet Midrash, now called the “Kolbuszowa Labor Camp.” ',
             'The Jewish community of Kolbuszowa was not reestablished after the war.',
             'Afterwards, thousands of peasants poured in to take property from the abandoned Jewish homes. ',
             'Only three Jews remained in the ghetto to run the cobbler`s cooperative, making suits and boots for the German Police. ',
             'New decrees were issued and shootings became commonplace.',
             'The other Kolbuszowa Jews in Rzeszów were deported to the Bełżec extermination camp.',
             'After the executions, Ehaus announced that all Jews in the Kreis would be evacuated to Rzeszów by June 25-27. ',
             'On April 28, 1942, the Gestapo arrested and shot more than 20 Jews according to a list prepared by a Ukrainian informant, who served in the police. ']


sent = sentences[23]

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

omit_verbs = ['was','had','did','aged']

print(sent)


#TEST


#FIND ROOTS
list_roots = find_roots(doc1)
list_verbs = find_verbs(doc1)

list_roots = remove_duplicates(list_roots)


for verb in list_verbs:
    for omit_verb in omit_verbs:
        if verb.orth_ == omit_verb:
            list_verbs.remove(verb)

list_objects = find_objects(doc1, list_verbs)
list_subjects = find_subjects(doc1)

#print('ROOTS',list_roots)

#print('ROOTS',list_roots)
#print('OBJECTS',list_objects)
#print('SUBJECTS',list_subjects)
#print('VERBS',list_verbs)

#Make Structure
for root in list_roots:
    triples = []
    subject = None


    for item in list_subjects:
        if item[1] == root:
            subject = item[0]

    if subject == None:
        #count subjects
        if len(list_subjects) ==1:
            subject = list_subjects[0][0]





    for item in list_objects:
        if item[1] == root:
            object = item[0]


    if subject == None:
        if root.head.pos in (NOUN, PRON) and root.head.head.dep_ == 'prep' :
            subject = root.head


    #PREDICATES
    for verb in list_verbs:
        if len(list_roots) == 1 and  (verb.dep_ != verb.head.dep_ or verb == verb.head)\
                or (len(list_roots) > 1 and  (verb.dep_ != verb.head.dep_ or len([word for word in list(verb.children) if word.dep_ in ('nsubj','nsubjpass')]) > 0)):

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

                        triples.append([[build_subject(subject)], [str(root) + ' ' +  str(child_word)], build_object(object),build_metadata(object)])

                        for item in list_objects:
                            if item[1] == verb:
                                object = item[0]

                        triples.append([[build_subject(subject)], [str(root) + ' ' +  str(verb)], build_object(object),build_metadata(object)])

                if get_dep_by_word(doc1,verb) in ('ROOT') and len([word for word in findLefts(doc1,verb) if word.dep_ == 'nsubjpass'])>0 \
                            and len([word for word in find(doc1,verb) if word.dep_ == 'advmod']) > 0:

                    for word in list(verb.subtree):
                        if word.dep_ == 'pobj':
                            object = word
                            break

                    if object.head.dep_ == 'prep':
                        triples.append([[build_subject(subject)], [str(root) + ' ' + str(list(find(doc1,verb))[0])+ ' ' + object.head.orth_], build_object(object),build_metadata(object)])
                    else:
                        triples.append([[build_subject(subject)], [str(root) + ' ' + str(list(find(doc1,verb))[0])], build_object(object),build_metadata(object)])

                elif get_dep_by_word(doc1,verb) in ('ROOT') and len([word for word in findLefts(doc1,verb) if word.dep_ == 'nsubjpass'])>0 \
                        and len([word for word in find(doc1,verb) if word.dep_ in ( 'advmod','prep','xcomp','conj')]) == 0:


                    for item in list_objects:
                        if item[1] == child_word:
                            object = item[0]

                    triples.append([[build_subject(subject)], [str(root)  ], build_object(object),build_metadata(object)])


                elif get_dep_by_word(doc1,verb) =='conj' and get_dep_by_word(doc1,child_word) == 'dobj':
                        object = None
                        for item in list_objects:
                            if item[1] == verb:
                                object = item[0]

                        triples.append([[build_subject(subject)], [str(verb)], build_object(object),build_metadata(object)])




                else:



                    if get_dep_by_word(doc1,child_word) == 'conj' and child_word.head.dep_ not in ('conj','ROOT','advcl') :

                        object=None

                        for item in list_objects:
                            if item[1] == root :
                                object = item[0]

                        if object == None:
                            triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object)])

                        for item in list_objects:
                            if item[1] == child_word:
                                object = item[0]

                        triples.append([[build_subject(subject)], [str(child_word)], build_object(object),build_metadata(object)])

                    elif get_dep_by_word(doc1,child_word) == 'conj' and child_word.head.dep_ not in ('conj','advcl') :


                        object=None
                        for item in list_objects:
                            if item[1] == root :
                                object = item[0]

                        if object == None and len(list_objects)>0:
                            triples.append([[build_subject(subject)], [str(root)], build_object([obj[0] for obj in list_objects if obj[1] == child_word][0]),build_metadata(object)])

                        for item in list_objects:
                            if item[1] == child_word:
                                object = item[0]

                        triples.append([[build_subject(subject)], [str(child_word)], build_object(object),build_metadata(object)])

                    elif get_dep_by_word(doc1,child_word) == 'conj' and child_word.head.dep_ == 'advcl' and child_word.head.pos == VERB:

                        object=None
                        for item in list_objects:
                            if item[1] == root :
                                object = item[0]
                        triples.append([[build_subject(subject)], [str(child_word.head)], build_object([obj[0] for obj in list_objects if obj[1] == child_word][0]),build_metadata(object)])

                        for item in list_objects:
                            if item[1] == child_word:
                                object = item[0]

                        triples.append([[build_subject(subject)], [str(child_word)], build_object(object),build_metadata(object)])


                    else:
                        if len(list(find(doc1,root)))>0:
                            object = None
                            #-----------------------------------RIGHT----------------------
                            for word in find(doc1,list(find(doc1,root))[0]):
                                if word.dep_ == 'pobj':
                                    object = word
                                    break

                            if list(find(doc1,root))[0].dep_ in ('prep','agent','prt'):

                                neg_words = [word for word in list(root.lefts) if word.dep_ == 'neg']
                                if  len(neg_words) > 0:
                                    triples.append([[build_subject(subject)], [neg_words[0].orth_ +' ' + str(root) +' ' + str(list(find(doc1,root))[0])], build_object(object),build_metadata(object)])
                                else:
                                    triples.append([[build_subject(subject)], [str(root) +' ' + str(list(find(doc1,root))[0])], build_object(object),build_metadata(object)])

                            else:
                                for obj in list_objects:

                                    if object!= None and obj[1] == root and obj[0].orth_ == object.orth_:
                                        triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object)])
                                    elif obj[1] == root: #newly added 5/5/2019
                                        triples.append([[build_subject(subject)], [str(root)], build_object(obj[0]),build_metadata(obj[0])])
                            #-----------------------------------LEFT----------------------
                            if len(list(findLefts(doc1,root)))>0:
                                for word in find(doc1,list(find(doc1,root))[0]):
                                    if word.dep_ == 'pobj':
                                        object = word
                                        break
                                if len(triples) == 0:
                                    if list(findLefts(doc1,root))[0].dep_ in ('prep','agent'):
                                        triples.append([[build_subject(subject)], [str(root) +'' + str(list(findLefts(doc1,root))[0])], object,build_metadata(object)])
                                    else:
                                        for obj in list_objects:
                                            if obj[1] == root and obj[0] == object:
                                                triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object)])

                        elif len(list(findLefts(doc1,root)))>0:

                            for word in findLefts(doc1,list(findLefts(doc1,root))[0]):
                                if word.dep_ == 'pobj':
                                    object = word
                                    break

                            if list(findLefts(doc1,root))[0].dep_ in ('prep','agent'):
                                triples.append([[build_subject(subject)], [str(root) +' ' + str(list(findLefts(doc1,root))[0])], build_object(object),build_metadata(object)])
                            else:
                                for obj in list_objects:
                                    if obj[1] == root and obj[0].orth_ == object .orth_:
                                        triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object)])




                    if get_dep_by_word(doc1,child_word) == 'advmod' and list(find(doc1,verb))[0] == child_word:

                        if (len(list(find(doc1,child_word))))>0:
                            if get_dep_by_word(doc1,list(find(doc1,child_word))[0] )  == 'prep':
                                #Find Object if any

                                for word in find(doc1,list(find(doc1,child_word))[0]):
                                    if word.dep_ == 'pobj':
                                        object = word
                                        break

                                triples.append([[build_subject(subject)], [str(root) + ' ' +  str(child_word) + ' ' + str(list(find(doc1,child_word))[0]) ], build_object(object),build_metadata(object)])


                    if get_dep_by_word(doc1,child_word) == 'prep' and  child_word.orth_ not in ('On', 'on','of'):

                        for word in list(find(doc1,child_word)):
                            if word.dep_ == 'pobj':
                                object = word
                                break

                        for obj in list_objects:
                            if obj[0] != None:
                                if object != None and obj[1] == root and obj[0].orth_ == object.orth_:
                                    neg_words = [word for word in list(root.lefts) if word.dep_ == 'neg']
                                    if  len(neg_words) > 0:
                                        triples.append([[build_subject(subject)], [neg_words[0].orth_+ ' ' +str(root) + ' ' +  str(child_word)  ], build_object(object),build_metadata(object)])
                                    else:
                                        triples.append([[build_subject(subject)], [str(root) + ' ' +  str(child_word)  ], build_object(object),build_metadata(object)])


    ([print(triple) for triple in form_triples(remove_duplicates(triples))])



#[to_nltk_tree(sent.root).pretty_print() for sent in doc1.sents]

