from itertools import chain

import nltk
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
