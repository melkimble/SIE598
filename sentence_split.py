import os

dir_in = "SelectedCorpus" # SET DIRECTORY WHERE TXT FILES TO SPLIT ARE LOCATED
dir_out = "SENTENCES" # SET OUTPUT DIRECTORY

# GET ALL FILES IN DIR_IN
list_ = [f for f in os.listdir(dir_in) if f.endswith(".txt")]
for file in list_:
    fbase = file[:-4] # BASENAME FOR OUTPUT FILE

    valid = [".", '."', ".\n", ".)", '.”'] # VALID ENDINGS TO SENTENCES - ADD MORE AS NEEDED
    invalid = ["Dr.", "Mr.", "Ms.", "Mrs.", "(e.g."] # WORDS THAT END WITH PERIODS THAT ARE NOT ENDS OF SENTENCES
    comment = "'''" # LINES THAT START AND END WITH THESE WILL BE EXCLUDED
    skip = False # FLAG
    to_split = []

    # READ IN FILE
    with open(f"{dir_in}/{file}", "r", encoding="UTF8") as f:
        lines = f.readlines()

    # DETERMINE WHICH LINES TO EXCLUDE BASED ON COMMENTS AND MOVE REST TO TO_SPLIT FOR PROCESSING
    for line in lines:
        if line.count(comment) == 2:
            pass
        elif line.count(comment) == 1 and line.startswith(comment):
            skip = True
        elif line.count(comment) == 1 and skip == True:
            skip = False
        elif skip == False:
            to_split.append(line)

    # EXAMINE EACH LINE AND SPLIT SENTENCES USING A BUFFER.  WHEN BUFFER EMPTIED, MOVE ON TO NEXT LINE.
    for line in to_split:
        buffer = line.split()
        sentences = []
        while buffer:
            for word in buffer:
                if word.endswith(tuple(valid)) and word not in invalid:
                    sentence = buffer[0:buffer.index(word)+1]
                    # print(sentence) # FOR DEBUGGING
                    sentences.append(" ".join(sentence))
                    del buffer[0:buffer.index(word)+1]
                    # print(buffer) # FOR DEBUGGING
                    break
        # WRITE SENTENCES IN LINE TO A FILE - ONE PER LINE
        with open(f"{dir_out}/{fbase}_sentences.txt", "a", encoding="UTF8") as f:
            for s in sentences:
                f.write(f"{s}\n")