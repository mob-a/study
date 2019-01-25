# -*- coding: utf-8 -*-

import sys
from collections import defaultdict
import math

def read_grammer(filename):
    terms = defaultdict(lambda:[])
    nonterms = defaultdict(lambda:[])
    with open(filename, "r") as f:
        for fline in f.readlines():
            fline = unicode(fline, "utf-8")
            fline = fline.rstrip(u"\r\n")
            src, dests, prob = fline.split(u"\t")
            prob = float(prob)

            dest_list = tuple(dests.split(u" "))
            if len(dest_list) == 1:
                terms[dests].append((src, prob))
            elif len(dest_list) == 2:
                nonterms[tuple(dest_list)].append((src, prob))
            else:
                raise Exception
    return (terms, nonterms)

class CKY():
    def __init__(self, terms, nonterms):
        self.terms = terms
        self.nonterms = nonterms

    def forget(self):
        self.best_tree = None

    def create_tree_list(self, words):
        word_num = len(words)

        phrase_dict = defaultdict(lambda:[])

        for word_idx, word in enumerate(words):
            for src, prob in self.terms[word]:
                phrase = (word_idx, word_idx, src, -math.log(prob), None, None)
                phrase_dict[(word_idx, word_idx)].append(phrase)

        for space in range(1, word_num):
            # sys.stderr.write("%s %s %s\n" % (str(space), str(word_num), str(len(phrase_dict))))
            for lstart in range(word_num - space):
                rend = lstart + space
 
                # (左端位置, 右端位置, ルートの非終端記号) が同じ部分木は、
                # 最低スコアのもののみ残す
                phrase_dict[(lstart, rend)] = self.get_best_subtrees(phrase_dict, lstart, rend)

        sentence_phrases = [p for p in phrase_dict[(0, word_num-1)] 
                            if (p[2] == u"S")]

        if len(sentence_phrases) == 0: 
            # 全部覆うSがない
            self.best_tree = None
        elif len(sentence_phrases) == 1:
            self.best_tree = sentence_phrases[0]
        else: 
            raise Exception

    def get_best_subtrees(self, phrase_dict, lstart, rend):
        min_score = {}
        for lend in range(lstart, rend):
            rstart = lend + 1  
            for lphrase in phrase_dict[(lstart, lend)]:
                for rphrase in phrase_dict[(rstart, rend)]:
                    for src, prob in self.nonterms[(lphrase[2] , rphrase[2])]:
                        score = -math.log(prob) + lphrase[3] + rphrase[3]

                        # rootの非終端記号ごとに、最低スコアのもののみ残す
                        if (src in min_score) and (score > min_score[src][3]):
                            continue
                        min_score[src] = (lstart, rend, src, score, lphrase, rphrase)
        return min_score.values()

    @classmethod
    def subtree_score(cls, subtree):
        score = subtree[3]
        if subtree[4] is not None:
            score += cls.subtree_score(subtree[4])
            score += cls.subtree_score(subtree[5])
        return score

    @classmethod
    def print_tree(cls, tree, words):
        tree_str = cls.simple_subtree_str(
            cls.simple_subtree(tree, words)
        )
        print tree_str.encode("utf-8")

    @classmethod
    def simple_subtree_str(cls, simple):
        if len(simple) == 2:
            return u"(%s %s)" % (simple[0], simple[1])
        elif len(simple) == 3:
            return u"(%s %s %s)" % (simple[0],
                                    cls.simple_subtree_str(simple[1]), 
                                    cls.simple_subtree_str(simple[2]))
        else:
            raise Exception

    @classmethod
    def simple_subtree(cls, subtree, words):
        if subtree[4] is None:
            return (subtree[2], words[subtree[0]])
        else:
            return (subtree[2], 
                    cls.simple_subtree(subtree[4], words), 
                    cls.simple_subtree(subtree[5], words))

terms, nonterms = read_grammer(sys.argv[1])
cky = CKY(terms, nonterms)

for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")

    cky.create_tree_list(words)
    if cky.best_tree is None:
        print "()"
    else:
        # print cky.best_tree[3]
        cky.print_tree(cky.best_tree, words)
    cky.forget()
