# REQUIRES ROOT ACCESS

from stanfordcorenlp import StanfordCoreNLP
import os

def dp_chunker(token, dp):
    # for triple in dp:
        # if triple[0] == "punct":
            # dp.remove(triple)
    root_index = dp[0][2]
    paths = []
    for triple in dp:
        step = triple[2]
        buffer = []
        while step != root_index:
            buffer.append(step)
            for triple in dp:
                if triple[2] == step:
                    step = triple[1]
                    if step not in buffer:
                        buffer.append(step)
        if len(buffer) > 0:
            paths.append(list(dict.fromkeys(buffer)))

    layer1 = [path[0] for path in paths if len(path) == 2]
    chunks = [[root_index]]
    for num in layer1:
        buffer = []
        for path in paths:
            if len(path) > 2 and num in path:
                buffer.extend(path)
        buffer = list(dict.fromkeys(buffer))
        if len(buffer) > 0:
            buffer.remove(root_index)
            buffer.sort()
            chunks.append(buffer)
        else:
            buffer.append(num)
            chunks.append(buffer)

    sentence_parts = [[triple[0], triple[2]] for triple in dp if triple[1] == root_index]
    sentence_parts.insert(0, [dp[0][0], dp[0][2]])

    sentence_chunks = []
    for part in sentence_parts:
        buffer = []
        for chunk in chunks:
            if part[1] in chunk:
                buffer.append(part[0].upper())
                buffer.append(" ".join([token[n - 1] for n in chunk]))
        sentence_chunks.append(buffer)

    return sentence_chunks

nlp = StanfordCoreNLP(os.path.expanduser(r"~/Desktop/Coursework/Spring 2019/SIE598/stanford-corenlp-full-2018-10-05"))
s_file_dir = os.path.expanduser(r"~/Desktop/Coursework/Spring 2019/SIE598/NLTK Test/kolbuszowa_full.txt")
filename = "kolbuszowa_dp_chunks.txt"

with open(s_file_dir) as file:
    s = [line[:line.rfind(".") + 1] for line in file]

token_dp_array = []
for sentence in s:
    s_num = s.index(sentence) + 1
    token = nlp.word_tokenize(sentence)
    dp = nlp.dependency_parse(sentence)
    token_dp_array.append([s_num, sentence, token, dp])

nlp.close()

with open(filename, "a") as file:
    for item in token_dp_array:
        chunks = dp_chunker(item[2], item[3])
        file.write(f"{item[0]}. {item[1]}\n")
        for chunk in chunks:
            file.write(f"--- {chunk[0]}: [{chunk[1]}]\n")
        file.write("\n")
        print(f"Sentence {item[0]} of {len(token_dp_array)} written to file")
print("Done")