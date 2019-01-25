# -*- coding: utf-8 -*-

import os
import sys
from Ngram import Ngram

ng = Ngram(1)
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ") + ["</s>"]
    ng.learn(words)

ng.write_model(sys.stdout)
