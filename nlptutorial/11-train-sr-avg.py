# -*- coding: utf-8 -*-
import sys
from ShiftReduce import ShiftReduceAvg
sr = ShiftReduceAvg()
correct_heads = {}
word_pos_list = []

for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")
    if line:
        node_id, word, orig, pos1, pos2, ext, head, label = line.split(u"\t")
    
        correct_heads[int(node_id)] = int(head)
        word_pos_list.append((word, pos1))
    else:
        sr.initialize(word_pos_list, train_flag=True, correct_heads=correct_heads)
        sr.shift_reduce()
        correct_heads = {}
        word_pos_list = []
    
# 最後に空行がない場合にも対応
if word_pos_list:
    sr.initialize(word_pos_list, train_flag=True, correct_heads=correct_heads)
    sr.shift_reduce()

sr.weight_average()
sr.write_weight(sys.argv[1])
