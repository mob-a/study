# -*- coding: utf-8 -*-

import os
import sys
from Ngram import Ngram

ng = Ngram(2)
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")    
    if words[-1] == u".":
        words = words[0:len(words)-1]
    words.insert(0, u"<s>")
    words.append(u"</s>")
    ng.learn(words)

ng.write_model(sys.stdout)
