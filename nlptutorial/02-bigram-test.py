# -*- coding: utf-8 -*-

import os
import sys
import math
from Ngram import Ngram

MAX_N=2
ng = Ngram(max_n=MAX_N, 
           all_word_num=long(10**6), 
           lambda_unigram=0.80, 
           lambda_ngram=0.80)

ng.read_model_from_file(sys.argv[1])

sum_log_prob = 0
all_ngram_count = 0
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")    
    if words[-1] == u".":
        words = words[0:len(words)-1]
    words.insert(0, u"<s>")
    words.append(u"</s>")

    log_prob = ng.get_sentence_prob(words)
    sum_log_prob += log_prob
    all_ngram_count += len(words) - MAX_N + 1
    
entropy = -1.0 * sum_log_prob * (1.0 / all_ngram_count)

print "%s" % str(entropy)
