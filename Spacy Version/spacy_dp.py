import spacy
from spacy.symbols import nsubj, VERB
from spacy import displacy


# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('en_core_web_sm')

#------------BEGIN-------------------------------
#sent = 'On the outbreak of World War II, around 2,500 Jews were residing in the town.'
text = 'On September 9, German officials selected 50 Jewish men to be sent to the forced labor camp in Rzeszów.'


doc = nlp(text)

# Analyze syntax
print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

for token in doc:
    print(token.text, token.dep_, token.head.text, token.head.pos_,
            [child for child in token.children])

# Finding a verb with a subject from below — good
verbs = set()
for possible_subject in doc:
    if possible_subject.dep == nsubj and possible_subject.head.pos == VERB:
        verbs.add(possible_subject.head)
print(verbs)

root = [token for token in doc if token.head == token][0]
subject = list(root.lefts)[0]
for descendant in subject.subtree:
    assert subject is descendant or subject.is_ancestor(descendant)
    print(descendant.text, descendant.dep_, descendant.n_lefts,
            descendant.n_rights,
            [ancestor.text for ancestor in descendant.ancestors])

span = doc[doc[4].left_edge.i: doc[4].right_edge.i + 1]
with doc.retokenize() as retokenizer:
    retokenizer.merge(span)
for token in doc:
    print(token.text, token.pos_, token.dep_, token.head.text)

# Since this is an interactive Jupyter environment, we can use displacy.render here
#displacy.serve(doc, style='dep', host='192.168.1.1:8080')
#print(displacy.render(doc, style="dep", page="true"))

for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)