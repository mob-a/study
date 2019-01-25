# -*- coding: utf-8 -*-
import sys
import numpy as np
from NeuralNetwork import NNNetwork

def get_feature_vec(words, ids):
    feature_vec = np.zeros(len(ids))
    for word in words:
        feature_id = u"UNI:" + word
        if feature_id in ids:
            feature_vec[ids[feature_id]] += 1
    return feature_vec

################
ids = NNNetwork.read_ids(sys.argv[1])
network = NNNetwork.read_nn_model(sys.argv[2], len(ids))

for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")

    feature_vec = get_feature_vec(words, ids)
    network.forward(feature_vec)
    print network.result_label()
