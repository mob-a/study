# -*- coding: utf-8 -*-

import sys
from LinearClassifier import Perceptron

percep = Perceptron()
percep.read_weight_from_file(sys.argv[1])

for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")

    feature = percep.get_feature(words)
    guessed_label = percep.classify(feature)

    print str(guessed_label)
 
