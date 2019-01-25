# -*- coding: utf-8 -*-

import numpy as np
from RecurrentNeuralNetwork import RNNNetwork

label_time_feature_vec = [
    (1, np.array([1.0, 2.0, 3.0, 4.0])),
    (2, np.array([-1.0, 2.0, -1.0, 2.0])),
    (0, np.array([1.0, -1.0, -1.0, 1.0])),
    (2, np.array([3.0, 3.0, -1.0, -2.0])),
    (1, np.array([-2.0, -2.0, 4.0, 3.0])),
]
time_feature_vec = [feature for label, feature in label_time_feature_vec]
labels = [label for label, feature in label_time_feature_vec]

end_time = len(time_feature_vec)
class_num = 3
feature_dim = 4
hidden_node_num = 2

print "################ initial #######################"
network = RNNNetwork(feature_dim=4, class_num=3, hidden_node_num=2)
network.forward(time_feature_vec)
print "===output_node==="
print "__weights__"
for c in range(class_num):
    print network.output_nodes[c].weights
print "__biases__"
for c in range(class_num):
    print network.output_nodes[c].bias
print "__class_probs__"
for t in range(end_time):
    print network.get_cached_class_prob(t)
print "__outputs__"
print network.class_outputs
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
for node_id, hidden_node in enumerate(network.hidden_nodes):
    print "===hidden_node:%s===" % str(node_id)
    print "__weights__"
    print hidden_node.weights
    print "__memory_weights__"
    print hidden_node.weights_memory
    print "__bias__"
    print hidden_node.bias
    print "__outputs__"
    print hidden_node.outputs
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

grad = network.gradient(labels, time_feature_vec, feature_dim)

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print "__grad__"

print grad

learn_rate = 0.1
network.update_weight(learn_rate, grad[0], grad[1], grad[2], grad[3], grad[4])
print "################ update #######################"
print "===output_node==="
print "__weights__"
for c in range(class_num):
    print network.output_nodes[c].weights
print "__biases__"
for c in range(class_num):
    print network.output_nodes[c].bias
print "__class_probs__"
for t in range(end_time):
    print network.get_cached_class_prob(t)
print "__outputs__"
print network.class_outputs
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
for node_id, hidden_node in enumerate(network.hidden_nodes):
    print "===hidden_node:%s===" % str(node_id)
    print "__weights__"
    print hidden_node.weights
    print "__memory_weights__"
    print hidden_node.weights_memory
    print "__bias__"
    print hidden_node.bias
    print "__outputs__"
    print hidden_node.outputs
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

grad = network.gradient(labels, time_feature_vec, feature_dim)

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print "__grad__"

print grad
