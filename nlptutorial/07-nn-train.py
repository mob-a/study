# -*- coding: utf-8 -*-
import sys
import numpy as np
from collections import defaultdict
from NeuralNetwork import NNNetwork

def get_feature(words):
    feature = {}
    for word in words:
        feature_id = u"UNI:" + word
        if feature_id not in feature:
            feature[feature_id] = 0
        feature[feature_id] += 1
    return feature

def to_feature_vec(label_features):
    ids = defaultdict(lambda: len(ids))


    for label, features in label_features:
        for feature_id in features.keys():
            ids[feature_id]

    label_feature_vecs = []
    for label, features in label_features:
        feature_vec = np.zeros(len(ids))
        for feature_id, value in features.iteritems():
            feature_vec[ids[feature_id]] = value
        label_feature_vecs.append((label, feature_vec))
    return ids, label_feature_vecs

################

label_features = []
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    label, words_str = line.split(u"\t")

    label = int(label)
    words = words_str.split(u" ")

    feature = get_feature(words)
    label_features.append((label, feature))

ids, label_feature_vecs = to_feature_vec(label_features)

layer_nodes = [2, 1]
network = NNNetwork(layer_nodes, len(ids))

iterate = 0
while iterate < 10:
    iterate += 1
    learn_rate = 0.1
    pre_error = 10.0**6

    for data_id, label_feature_vec in enumerate(label_feature_vecs):
        label = label_feature_vec[0]
        feature_vec = label_feature_vec[1]

        network.forward(feature_vec)
        network.error_backward(label)
        network.update(feature_vec, learn_rate)

        if abs(network.final_error()) > pre_error:
            learn_rate = learn_rate * 0.9
        pre_error = network.final_error()


network.write_weight_ids(sys.argv[1], ids)
