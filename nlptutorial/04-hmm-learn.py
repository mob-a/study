# -*- coding: utf-8 -*-
import sys
from HMM import HMM

hmm = HMM()
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    word_pos_list = [tuple(word_pos.split(u"_")) for word_pos in line.split(u" ")]

    hmm.learn(word_pos_list, start_pos=u"<s>", end_pos=u"</s>")


hmm.write_model(sys.stdout)
