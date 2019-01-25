# -*- coding: utf-8 -*-

import numpy as np
import sys
from collections import defaultdict
from RecurrentNeuralNetwork import RNNNetwork
def get_feature(words):
    feature = {}
    for word in words:
        feature_id = u"UNI:" + word
        if feature_id not in feature:
            feature[feature_id] = 0
        feature[feature_id] += 1
    return feature

def to_feature_vec(word_poses_list):
    word_ids = defaultdict(lambda: len(word_ids))
    pos_ids = defaultdict(lambda: len(pos_ids))

    for word_poses in word_poses_list:
        for word, pos in word_poses:
            feature_id = u"UNI:" + word
            word_ids[feature_id]
            pos_ids[pos]

    word_dim = len(word_ids)

    label_vector_sequence_list = []
    for word_poses in word_poses_list:
        label_vector_sequence = []
        for word, pos in word_poses:
            vector = np.zeros(word_dim)

            feature_id = u"UNI:" + word
            vector[word_ids[feature_id]] = 1.0

            label = pos_ids[pos]
            label_vector_sequence.append((label, vector))

        label_vector_sequence_list.append(label_vector_sequence)
    return word_ids, pos_ids, label_vector_sequence_list


word_poses_list = []
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    word_poses = []
    for word_pos in line.split(u" "):
        word, pos = word_pos.split(u"_")
        word_poses.append((word, pos))
    word_poses_list.append(word_poses)


word_ids, pos_ids, label_vector_sequence_list = to_feature_vec(word_poses_list)

feature_dim = len(word_ids)
class_num = len(pos_ids)

learn_rate = 0.4
hidden_node_num = 2
network = RNNNetwork(feature_dim=feature_dim, 
                     class_num=class_num, 
                     hidden_node_num=hidden_node_num)

iterate = int(sys.argv[2])
for it in range(iterate):
    for label_vector_sequence in label_vector_sequence_list:
        vectors = [vector for label, vector in label_vector_sequence]
        labels = [label for label, vector in label_vector_sequence]

        network.forget()
        network.forward(vectors)
        grad = network.gradient(labels, vectors, feature_dim)
        network.update_weight(learn_rate,
                              grad[0], grad[1], grad[2], grad[3], grad[4])


basefilename = sys.argv[1]

with open(basefilename + ".word.ids", "w") as writer:
    for word in sorted(word_ids.keys(), key=lambda k:word_ids[k]):
        dim = word_ids[word]
        writer.write("%s\t%s\n" % (word.encode("utf-8"), str(dim)))
    
with open(basefilename + ".pos.ids", "w") as writer:
    for pos in sorted(pos_ids.keys(), key=lambda k:pos_ids[k]):
        dim = pos_ids[pos]
        writer.write("%s\t%s\n" % (pos.encode("utf-8"), str(dim)))

with open(basefilename + ".weights", "w") as writer:
    for node_id, node in enumerate(network.hidden_nodes):
        weight_list = ["%s:%s" % (str(wdim), str(weight)) 
                       for wdim, weight in enumerate(node.weights)]
        weight_str = "_".join(weight_list)

        weight_memory_list = ["%s:%s" % (str(wdim), str(weight)) 
                              for wdim, weight in enumerate(node.weights_memory)]
        weight_memory_str = "_".join(weight_memory_list)

        bias_str = "-1:" + str(node.bias)
        
        writer.write("HW\t%s\t%s\n" % (
            str(node_id), weight_str))
        writer.write("HM\t%s\t%s\n" % (
            str(node_id), weight_memory_str))
        writer.write("HB\t%s\t%s\n" % (
            str(node_id), bias_str))

    for node_id, node in enumerate(network.output_nodes):
        weight_list = ["%s:%s" % (str(wdim), str(weight)) 
                       for wdim, weight in enumerate(node.weights)]
        weight_str = "_".join(weight_list)

        bias_str = "-1:" + str(node.bias)
        
        writer.write("OW\t%s\t%s\n" % (
            str(node_id), weight_str))
        writer.write("OB\t%s\t%s\n" % (
            str(node_id), bias_str))

