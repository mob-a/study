# -*- coding: utf-8 -*-

import sys
from LinearClassifier import OnlineSVM
def do_train(label_features, margin, c, basefilename):
    osvm = OnlineSVM(c=c, margin=margin)

    for label, feature in label_features:
        confidence = label * osvm.inner_prod_self(feature)
    
        if confidence < osvm.margin:
            osvm.update_weight(feature, label)
    filename = "%s_%s_%s" % (basefilename, str(margin), str(c))
    osvm.write_weight_to_file(filename)

osvm_tmp = OnlineSVM(c=0, margin=0)
basefilename = sys.argv[1]
label_features = []
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    label, words_str = line.split(u"\t")

    label = int(label)
    words = words_str.split(u" ")

    feature = osvm_tmp.get_feature(words)
    label_features.append((label, feature))
osvm_tmp = None

MARGINS = [100.0, 10.0, 1.0, 0.1, 0]
CS = [0.001, 0.0001, 0.00001, 0.000001, 0]
for margin in MARGINS:
    for c in CS:
        do_train(label_features, margin, c, basefilename)
