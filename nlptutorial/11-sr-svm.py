# -*- coding: utf-8 -*-
import sys
from ShiftReduceSVM import ShiftReduceSVM

sr = ShiftReduceSVM()
correct_heads = {}
word_pos_list = []
with open(sys.argv[1], "r") as train_reader:
    i = 0
    for line in train_reader.readlines():
        line = unicode(line, "utf-8")
        line = line.rstrip(u"\r\n")
    
        if line:
            node_id, word, orig, pos1, pos2, ext, head, label = line.split(u"\t")
    
            correct_heads[int(node_id)] = int(head)
            word_pos_list.append((word, pos1))
        else:
            sr.initialize(word_pos_list, train_flag=True, correct_heads=correct_heads)
            sr.shift_reduce_train()
            correct_heads = {}
            word_pos_list = []
    
    # 最後に空行がない場合にも対応
    if word_pos_list:
        sr.initialize(word_pos_list, train_flag=True, correct_heads=correct_heads)
        sr.shift_reduce_train()        
sr.learn_classifier()

word_pos_list = []
all_data_list = []
with open(sys.argv[2], "r") as test_reader:
    for line in test_reader.readlines():
        line = unicode(line, "utf-8")
        line = line.rstrip(u"\r\n")

        if line:
            node_id, word, orig, pos1, pos2, ext, head, label = line.split(u"\t")
    
            word_pos_list.append((word, pos1))
            all_data_list.append((node_id, word, orig, pos1, pos2, ext))
        else:
            sr.initialize(word_pos_list)
            sr.shift_reduce_test()
            sr.write_tree(sys.stdout, all_data_list)
            all_data_list = []
            word_pos_list = []
    
    # 最後に空行がない場合にも対応
    if word_pos_list:
        sr.initialize(word_pos_list)
        sr.shift_reduce_test()
        sr.write_tree(sys.stdout, all_data_list)
