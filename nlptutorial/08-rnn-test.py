# -*- coding: utf-8 -*-

import numpy as np
import sys
from collections import defaultdict
from RecurrentNeuralNetwork import RNNNetwork

def read_ids(filename):
    ids = {}
    with open(filename, "r") as f:
        for fline in f.readlines():
            fline = unicode(fline, "utf-8")
            fline = fline.rstrip(u"\r\n")
            feature_id, dim = fline.split(u"\t")
            dim = int(dim)
            ids[feature_id] = dim
    return ids

def read_rnn_model(filename, feature_dim):

    # ノード数を知る
    hidden_node_id_max = -1
    output_node_id_max = -1
    with open(filename, "r") as f:
        for fline in f.readlines():
            fline = unicode(fline, "utf-8")
            fline = fline.rstrip(u"\r\n")
            weight_type, node_id, weights = fline.split(u"\t")

            node_id = int(node_id)
            if weight_type == u"HW":
                if hidden_node_id_max < node_id:
                    hidden_node_id_max = node_id

            if weight_type == u"OW":
                if output_node_id_max < node_id:
                    output_node_id_max = node_id

    class_num = output_node_id_max + 1
    hidden_node_num = hidden_node_id_max + 1
    network = RNNNetwork(feature_dim=feature_dim, 
                         class_num=class_num,
                         hidden_node_num=hidden_node_num)


    # weightsを設定
    with open(filename, "r") as f:
        for fline in f.readlines():
            fline = unicode(fline, "utf-8")
            fline = fline.rstrip(u"\r\n")
            weight_type, node_id, weights = fline.split(u"\t")

            node_id = int(node_id)

            if weight_type == u"HB":
                b, bias = weights.split(u":")
                network.hidden_nodes[node_id].bias = float(bias)
                continue
            elif weight_type == "OB":
                b, bias = weights.split(u":")
                network.output_nodes[node_id].bias = float(bias)
                continue

            if weight_type == u"HW":
                vec = np.zeros(feature_dim)
            elif weight_type == u"HM":
                vec = np.zeros(hidden_node_num)
            elif weight_type == u"OW":
                vec = np.zeros(hidden_node_num)
            else:
                raise Exception

            for dim_value in weights.split(u"_"):
                dim, value = dim_value.split(u":")
                vec[int(dim)] = float(value)

            if weight_type == u"HW":
                network.hidden_nodes[node_id].weights = vec
            elif weight_type == u"HM":
                network.hidden_nodes[node_id].weights_memory = vec
            elif weight_type == u"OW":
                network.output_nodes[node_id].weights = vec
            else:
                raise Exception

    return network


def get_feature_vec_sequence(words, ids):
    vector_sequence = []
    for word in words:
        feature_id = u"UNI:" + word
        vector = np.zeros(len(ids))

        if feature_id in ids:
            vector[ids[feature_id]] = 1.0
        vector_sequence.append(vector)

    return vector_sequence

word_ids = read_ids(sys.argv[1] + ".word.ids")
pos_ids = read_ids(sys.argv[1] + ".pos.ids")
rev_pos_ids = dict((v, k) for k, v in pos_ids.iteritems())
network = read_rnn_model(sys.argv[1] + ".weights", len(word_ids))

for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")

    vector_sequence = get_feature_vec_sequence(words, word_ids)

    network.forget()
    network.forward(vector_sequence)

    output_poses = [rev_pos_ids[y] for y in network.class_outputs]
    print u" ".join(output_poses).encode("utf-8")
