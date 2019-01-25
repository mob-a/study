# -*- coding: utf-8 -*-
import numpy as np
from NeuralNetwork import NNNetwork
print "#####################################"
label_feature_vecs = [
    (1, np.array([1.0,1.0])),
    (1, np.array([-1.0,-1.0])),
    (1, np.array([2.0,0.0])),
    (1, np.array([0.0, 2.0])),
    (1, np.array([-1.0,-1.0])),

    (-1, np.array([1.0,-1.0])),
    (-1, np.array([-1.0,1.0])),
    (-1, np.array([2.0,-2.0])),
    (-1, np.array([-2.0,2.0])),
    (-1, np.array([0.0,0.0])),
]

layer_nodes = [2, 1]
network = NNNetwork(layer_nodes, 2)

iterate = 0
while iterate < 2000:
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

        print "iterate:%s dat:%s result:%s error:%s" % (str(iterate),
                                                        str(data_id),
                                                        str(network.result_label()==label), 
                                                        str(network.final_error()))

print "#####################################"
label_feature_vecs = [
    (1, np.array([0.3,0.3])),
    (1, np.array([0.2,-0.4])),
    (-1, np.array([-0.5, -0.8])),
    (-1, np.array([-0.2, -0.4])),
    (1, np.array([0.5,0.2])),
    (1, np.array([-0.2,0.4])),
    (-1, np.array([-0.6, -0.3])),
    (-1, np.array([-0.1,-0.1])),
]

layer_nodes = [4, 2, 3, 1]
network = NNNetwork(layer_nodes, 2)

iterate = 0
while iterate < 2000:
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

        print "iterate:%s dat:%s result:%s error:%s" % (str(iterate),
                                                        str(data_id),
                                                        str(network.result_label()==label), 
                                                        str(network.final_error()))
