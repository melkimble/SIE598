import datetime
import itertools
import json
import os
from copy import copy

import spacy
from dateutil.parser import parse
from nltk import Tree
from spacy.symbols import VERB, NOUN, PRON
from sutime import sutime, SUTime

from Util import to_nltk_tree, find_roots, get_tag_by_word, get_dep_by_word, get_subtree_of, find_objects, find_verbs, \
    find_subjects, find, findLefts, remove_duplicates, build_object, build_subject, build_metadata, form_triples, \
    cleanup, last_day_of_month
import re

#-----------------------------------------------------------------------------------------------------------------------
#LOAD THE SENTENCES

dir_in = "SENTENCES" # SET DIRECTORY WHERE TXT FILES TO SPLIT ARE LOCATED

list_ = [f for f in os.listdir(dir_in) if f.endswith(".txt")]
#SUTime
os.environ['CLASSPATH'] = r'C:\Users\Iranga\workspace\NLP_SF\stanford-ner-2018-10-16\stanford-ner-2018-10-16'
jar_files = os.path.join(os.path.dirname(__file__), 'jars')
sutime = SUTime(jars=jar_files, mark_time_ranges=True, include_range=True)

nlp = spacy.load("")

for file in list_:
    fbase = file[:-4] # BASENAME FOR OUTPUT FILE

    valid = [".", '."', ".\n", ".)", '.”'] # VALID ENDINGS TO SENTENCES - ADD MORE AS NEEDED
    invalid = ["Dr.", "Mr.", "Ms.", "Mrs.", "(e.g."] # WORDS THAT END WITH PERIODS THAT ARE NOT ENDS OF SENTENCES
    comment = "'''" # LINES THAT START AND END WITH THESE WILL BE EXCLUDED
    skip = False # FLAG
    to_split = []

    filepath = f"{dir_in}/{fbase}.txt"
    list_sentences = []
    with open(filepath,encoding="utf8") as file:
         for line in file:
             list_sentences.append([line[:line.rfind(".") + 1]])



    sentences = list_sentences

    reference_date = '1939-9-1'

    for sent in sentences:
        sent = sent[0]
        #sent = sentences[26]
        meta_date =''
        object = None
        print("---------------------------------------------------------")

        jsn = json.dumps(sutime.parse(sent, reference_date=reference_date), sort_keys=True, indent=4)
        d = json.loads(jsn)

        if (len(d) >0):
            if len(list(cleanup(str(d[0]['value']))))>0:
                su_date = list(cleanup(str(d[0]['value'])))[0]

                match = re.match(r'.*([1-3][0-9]{3})', sent)
                if (match == None):
                    if su_date < parse(reference_date) and  (parse(reference_date) - su_date).days > 30:
                        su_date = su_date + datetime.timedelta(days=365)
                        meta_date = str(su_date)
                    elif su_date < parse(reference_date) and  (parse(reference_date) - su_date).days <= 30:
                        su_date = su_date + datetime.timedelta(days=365)
                        meta_date = str(last_day_of_month(su_date))


                if meta_date == '':
                    meta_date = str(datetime.date(su_date.year, su_date.month, su_date.day))

                reference_date = str(su_date)
            else:
                meta_date = str(d[0]['value'])

            #sent = sent.replace(d[0]['text'],d[0]['value'])

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

                                triples.append([[build_subject(subject)], [str(root) + ' ' +  str(child_word)], build_object(object),build_metadata(object),meta_date,[object]])

                                for item in list_objects:
                                    if item[1] == verb:
                                        object = item[0]

                                triples.append([[build_subject(subject)], [str(root) + ' ' +  str(verb)], build_object(object),build_metadata(object),meta_date,[object]])

                        if get_dep_by_word(doc1,verb) in ('ROOT') and len([word for word in findLefts(doc1,verb) if word.dep_ == 'nsubjpass'])>0 \
                                    and len([word for word in find(doc1,verb) if word.dep_ == 'advmod']) > 0:

                            for word in list(verb.subtree):
                                if word.dep_ == 'pobj':
                                    object = word
                                    break

                            if object.head.dep_ == 'prep':
                                triples.append([[build_subject(subject)], [str(root) + ' ' + str(list(find(doc1,verb))[0])+ ' ' + object.head.orth_], build_object(object),build_metadata(object),meta_date,[object]])
                            else:
                                triples.append([[build_subject(subject)], [str(root) + ' ' + str(list(find(doc1,verb))[0])], build_object(object),build_metadata(object),meta_date,[object]])

                        elif get_dep_by_word(doc1,verb) in ('ROOT') and len([word for word in findLefts(doc1,verb) if word.dep_ == 'nsubjpass'])>0 \
                                and len([word for word in find(doc1,verb) if word.dep_ in ( 'advmod','prep','xcomp','conj')]) == 0:

                            object = None
                            for item in list_objects:
                                if item[1] == verb:
                                    object = item[0]
                            triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object),meta_date,[object]])



                        elif get_dep_by_word(doc1,verb) =='conj' and get_dep_by_word(doc1,child_word) == 'dobj':
                            object = None
                            for item in list_objects:
                                if item[1] == verb:
                                    object = item[0]

                            triples.append([[build_subject(subject)], [str(verb)], build_object(object),build_metadata(object),meta_date,[object]])


                        else:
                            #NEWLY ADDED 5/6/2019
                            if get_dep_by_word(doc1,child_word) == 'ccomp' and child_word.head.dep_  in ('ROOT') and len([word for word in list(child_word.lefts) if word.dep_ == 'auxpass']) == 0 :

                                object=None

                                for item in list_objects:
                                    if item[1] == root :
                                        object = item[0]
                                        break

                                if object == None:
                                    triples.append([[build_subject(subject)], [str(child_word.head) +' ' + str(child_word)], build_object(object),build_metadata(object),meta_date,[object]])


                            elif get_dep_by_word(doc1,child_word) == 'ccomp' and child_word.head.dep_  in ('ROOT') and len([word for word in list(child_word.lefts) if word.dep_ == 'auxpass']) > 0 :

                                object=None

                                for item in list_objects:
                                    if item[1] == root :
                                        object = item[0]
                                        break

                                if object == None:
                                    triples.append([[build_subject(subject)], [str(child_word.head)], build_object(object),build_metadata(object),meta_date,[object]])


                            if get_dep_by_word(doc1,child_word) == 'conj' and child_word.head.dep_ not in ('conj','ROOT','advcl') :

                                object=None

                                for item in list_objects:
                                    if item[1] == root :
                                        object = item[0]
                                        break

                                if object == None:
                                    triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object),meta_date,[object]])

                                for item in list_objects:
                                    if item[1] == child_word:
                                        object = item[0]
                                        break

                                triples.append([[build_subject(subject)], [str(child_word)], build_object(object),build_metadata(object),meta_date,[object]])

                            elif get_dep_by_word(doc1,child_word) == 'conj' and child_word.head.dep_ not in ('conj','advcl') :
                                object=None
                                for item in list_objects:
                                    if item[1] == root :
                                        object = item[0]

                                        break

                                if object == None and len(list_objects)>0 and len([obj[0] for obj in list_objects if obj[1] == root]) > 0:
                                    if len([word for word in list(root.lefts) if word.dep_ == 'auxpass'])>0:
                                        triples.append([[build_subject(subject)], [str([word for word in list(root.lefts) if word.dep_ == 'auxpass'][0]) + ' ' + str(root)], build_object([obj[0] for obj in list_objects if obj[1] == root][0]),build_metadata(object),meta_date,
                                                        [[obj[0] for obj in list_objects if obj[1] == root][0]]])
                                    else:
                                        triples.append([[build_subject(subject)], [str(root)], build_object([obj[0] for obj in list_objects if obj[1] == root][0]),build_metadata(object),meta_date,
                                                        [[obj[0] for obj in list_objects if obj[1] == root][0]]])


                                elif object == None and len(list_objects)>0 and len([obj[0] for obj in list_objects if obj[1] == root]) == 0:
                                    if len([word for word in list(root.lefts) if word.dep_ == 'auxpass'])>0:
                                        triples.append([[build_subject(subject)], [str([word for word in list(root.lefts) if word.dep_ == 'auxpass'][0]) +' ' + str(root)], build_object(object),build_metadata(object),meta_date,[object]])
                                    else:
                                        triples.append([[build_subject(subject)], [ str(root)], build_object(object),build_metadata(object),meta_date,[object]])

                                object=None
                                for item in list_objects:
                                    if item[1] == child_word:
                                        object = item[0]
                                        break

                                triples.append([[build_subject(subject)], [str(child_word)], build_object(object),build_metadata(object),meta_date,[object]])

                            elif get_dep_by_word(doc1,child_word) == 'ccomp' and child_word.head.dep_ in ('conj','advcl') :

                                #print(child_word)
                                object=None

                                for item in list_objects:
                                    if item[1] == child_word.head:
                                        object = item[0]
                                        break

                                triples.append([[build_subject(subject)], [str(child_word.head)+ ' ' + str(child_word)], build_object(object),build_metadata(object),meta_date,[object]])

                            elif get_dep_by_word(doc1,child_word) == 'conj' and child_word.head.dep_ == 'advcl' and child_word.head.pos == VERB:

                                object=None
                                for item in list_objects:
                                    if item[1] == root :
                                        object = item[0]
                                        break
                                triples.append([[build_subject(subject)], [str(child_word.head)], build_object([obj[0] for obj in list_objects if obj[1] == child_word][0]),
                                                build_metadata(object),meta_date,[[obj[0] for obj in list_objects if obj[1] == child_word][0]]])

                                object=None
                                for item in list_objects:
                                    if item[1] == child_word:
                                        object = item[0]
                                        break

                                triples.append([[build_subject(subject)], [str(child_word)], build_object(object),build_metadata(object),meta_date,[object]])


                            else:
                                object = None
                                if len(list(find(doc1,root)))>0:

                                    #-----------------------------------RIGHT----------------------
                                    for word in find(doc1,list(find(doc1,root))[0]):
                                        if word.dep_ == 'pobj':
                                            object = word
                                            break

                                    if list(find(doc1,root))[0].dep_ in ('prep','agent','prt'):

                                        neg_words = [word for word in list(root.lefts) if word.dep_ == 'neg']
                                        if  len(neg_words) > 0:
                                            triples.append([[build_subject(subject)], [neg_words[0].orth_ +' ' + str(root) +' ' + str(list(find(doc1,root))[0])], build_object(object),build_metadata(object),meta_date,[object]])
                                        else:
                                            triples.append([[build_subject(subject)], [str(root) +' ' + str(list(find(doc1,root))[0])], build_object(object),build_metadata(object),meta_date,[object]])

                                    else:
                                        for obj in list_objects:

                                            if object!= None and obj[1] == root and obj[0].orth_ == object.orth_:
                                                triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object),meta_date,[object]])
                                            elif obj[1] == root: #newly added 5/5/2019
                                                triples.append([[build_subject(subject)], [str(root)], build_object(obj[0]),build_metadata(obj[0]),meta_date,[obj[0]]])
                                    #-----------------------------------LEFT----------------------
                                    if len(list(findLefts(doc1,root)))>0:
                                        object=None
                                        for word in find(doc1,list(find(doc1,root))[0]):
                                            if word.dep_ == 'pobj':
                                                object = word
                                                break
                                        if len(triples) == 0:
                                            if list(findLefts(doc1,root))[0].dep_ in ('prep','agent') and list(findLefts(doc1,root))[0].orth_ not in ('After','Before','Within'):
                                                triples.append([[build_subject(subject)], [str(root) +' ' + str(list(findLefts(doc1,root))[0])], object,build_metadata(object),meta_date,[object]])
                                            else:
                                                for obj in list_objects:
                                                    if obj[1] == root and obj[0] == object:
                                                        triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object),meta_date,[object]])

                                elif len(list(findLefts(doc1,root)))>0:

                                    object=None
                                    for word in findLefts(doc1,list(findLefts(doc1,root))[0]):
                                        if word.dep_ == 'pobj':
                                            object = word
                                            break

                                    if list(findLefts(doc1,root))[0].dep_ in ('prep','agent'):
                                        triples.append([[build_subject(subject)], [str(root) +' ' + str(list(findLefts(doc1,root))[0])], build_object(object),build_metadata(object),meta_date,[object]])
                                    else:
                                        for obj in list_objects:
                                            if obj[1] == root and obj[0].orth_ == object .orth_:
                                                triples.append([[build_subject(subject)], [str(root)], build_object(object),build_metadata(object),meta_date,[object]])




                            if get_dep_by_word(doc1,child_word) == 'advmod' and list(find(doc1,verb))[0] == child_word:

                                if (len(list(find(doc1,child_word))))>0:
                                    if get_dep_by_word(doc1,list(find(doc1,child_word))[0] )  == 'prep':
                                        #Find Object if any
                                        object=None
                                        for word in find(doc1,list(find(doc1,child_word))[0]):
                                            if word.dep_ == 'pobj':
                                                object = word
                                                break



                            if get_dep_by_word(doc1,child_word) == 'prep' and  child_word.orth_ not in ('On', 'on','of'):
                                object=None
                                for word in list(find(doc1,child_word)):
                                    if word.dep_ == 'pobj':
                                        object = word
                                        break

                                for obj in list_objects:
                                    if obj[0] != None:
                                        if object != None and obj[1] == root and obj[0].orth_ == object.orth_:
                                            neg_words = [word for word in list(root.lefts) if word.dep_ == 'neg']
                                            if  len(neg_words) > 0:
                                                triples.append([[build_subject(subject)], [neg_words[0].orth_+ ' ' +str(root) + ' ' +  str(child_word)  ],
                                                                build_object(object),build_metadata(object),meta_date, [object]])
                                            else:
                                                triples.append([[build_subject(subject)], [str(root) + ' ' +  str(child_word)  ], build_object(object),build_metadata(object),meta_date,[object]])



            ([print(triple) for triple in form_triples(remove_duplicates(triples))])

        #[to_nltk_tree(sent.root).pretty_print() for sent in doc1.sents]

