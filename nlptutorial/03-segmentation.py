# -*- coding: utf-8 -*-

import sys
import math
from Ngram import Ngram
from ViterbiGraph import NodeMap, PathMap, ViterbiGraph
ng = Ngram(max_n=1,lambda_unigram=0.80,all_word_num=long(10**6))

LARGE_SCORE = 10**10

ng.read_model_from_file(sys.argv[1])

def get_all_candidates(chars, idx, unigram_model):
    # TODO: trie使うべき

    # 一文字
    candidates = [chars[idx]]

    # 2文字以上でユニグラムモデルに含まれるもの
    for end_idx in xrange(idx+2, len(chars)+1):
        substring = u"".join(chars[idx:end_idx])
        if tuple([substring]) in unigram_model:
            candidates.append(substring)

    return candidates

for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    chars = list(line)

    viterbigraph = ViterbiGraph(NodeMap(), PathMap())

    viterbigraph.node_map.set_node(0, 0, min_score=0.0)
    viterbigraph.set_start_node_id(0)
    for char_idx in xrange(1, len(chars)+1):
        viterbigraph.node_map.set_node(char_idx, char_idx)
    viterbigraph.set_end_node_id(len(chars))

    for char_idx in xrange(len(chars)):
        candidates = get_all_candidates(chars, char_idx, ng.ngram_model[1])

        for word in candidates:
            next_start_idx = char_idx + len(word)
            score = -1.0 * math.log(ng.get_unigram_prob(word), 2.0)
            viterbigraph.path_map.set_path(char_idx, next_start_idx, score)

    viterbigraph.solve()
    best_path = viterbigraph.get_best_path()

    segments = [u"".join(chars[best_path[i-1]:best_path[i]]) for i in range(1, len(best_path))]
    print u" ".join(segments).encode("utf-8")
