# -*- coding: utf-8 -*-

import os
import sys
import math
from Ngram import Ngram

ng = Ngram(max_n=1, 
           all_word_num=long(10**6), 
           lambda_unigram=0.95)

ng.read_model_from_file(sys.argv[1])

sum_log_prob = 0.0
all_word_count = 0
covered_count = 0
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ") + [u"</s>"]

    sum_log_prob += ng.get_sentence_prob(words)
    covered_count += ng.covered(words)
    all_word_count += len(words)

entropy = -1.0 * sum_log_prob * (1.0 / all_word_count)
ppl = 2.0 ** entropy 

coverage = float(covered_count) / all_word_count
print "ENTROPY: %s" % str(entropy)
print "PPL: %s" % str(ppl)
print "COVERAGE: %s" % str(coverage)
