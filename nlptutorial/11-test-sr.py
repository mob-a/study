# -*- coding: utf-8 -*-
import sys
from ShiftReduce import ShiftReduce

sr = ShiftReduce()
sr.read_weight(sys.argv[1])

word_pos_list = []
all_data_list = []
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    if line:
        node_id, word, orig, pos1, pos2, ext, head, label = line.split(u"\t")

        word_pos_list.append((word, pos1))
        all_data_list.append((node_id, word, orig, pos1, pos2, ext))
    else:
        sr.initialize(word_pos_list)
        sr.shift_reduce()
        sr.write_tree(sys.stdout, all_data_list)
        all_data_list = []
        word_pos_list = []

# 最後に空行がない場合にも対応
if word_pos_list:
    sr.initialize(word_pos_list)
    sr.shift_reduce()
    sr.write_tree(sys.stdout, all_data_list)
