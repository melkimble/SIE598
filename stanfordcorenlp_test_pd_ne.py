# NEEDS ROOT ACCESS TO CONNECT WITH CORENLP

from stanfordcorenlp import StanfordCoreNLP
import os
import pandas as pd
from pandas import ExcelWriter

nlp = StanfordCoreNLP(os.path.expanduser(r"~/Desktop/Coursework/Spring 2019/SIE598/stanford-corenlp-full-2018-10-05"))

s_file_dir = os.path.expanduser(r"~/Desktop/Coursework/Spring 2019/SIE598/NLTK Test/kolbuszowa_full.txt")
f_rootname = (s_file_dir[:s_file_dir.rfind(".")])[s_file_dir.rfind("/") + 1:]

with open(s_file_dir) as file:
    s = [line[:line.rfind(".") + 1] for line in file]

ne_array = []

for sentence in s:
    s_num = s.index(sentence) + 1
    ne = nlp.ner(sentence)
    for s_tuple in ne:
        if len(s_tuple[1]) > 1:
            ne_array.append([s_tuple[0], s_tuple[1], s_num])

nlp.close()

temp = []
for i in range(len(ne_array)):
    temp.append(ne_array[i][:2])
unique_ne = []
for entry in temp:
    if entry not in unique_ne:
        unique_ne.append(entry)

df0 = pd.DataFrame({"Index": [s.index(sentence) + 1 for sentence in s],
                    "Sentence": [sentence for sentence in s]})
df1 = pd.DataFrame({"Word": [array_tuple[0] for array_tuple in ne_array],
                   "NE": [array_tuple[1] for array_tuple in ne_array],
                   "Sentence": [array_tuple[2] for array_tuple in ne_array]})
df2 = pd.DataFrame({"Word": [array_tuple[0] for array_tuple in unique_ne],
                   "NE": [array_tuple[1] for array_tuple in unique_ne]})

writer = ExcelWriter(f"{f_rootname}.xlsx")
df0.to_excel(writer, "Sentences", index=False, columns=["Index", "Sentence"])
df1.to_excel(writer, "NE's", index=False, columns=["Word", "NE", "Sentence"])
df2.to_excel(writer, "Unique NE's", index=False, columns=["Word", "NE"])
writer.save()