# -*- coding: utf-8 -*-

import sys
from LinearClassifier import Perceptron
percep = Perceptron()
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    label, words_str = line.split(u"\t")

    label = int(label)
    words = words_str.split(u" ")

    feature = percep.get_feature(words)
    guessed_label = percep.classify(feature)
    
    if label != guessed_label:
        percep.update_weight(feature, label)

percep.write_weight(sys.stdout)
