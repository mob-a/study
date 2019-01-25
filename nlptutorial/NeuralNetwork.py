# -*- coding: utf-8 -*-
import numpy as np

class NNNode():
    def __init__(self, feature_dim, random=True):
        # 初期値をランダムに
        if random:
            self.weights = (np.random.rand(feature_dim) - 0.5) * 0.2
            self.weight_bias = (np.random.rand() - 0.5) * 0.2
        else:
            self.weights = np.zeros(feature_dim)
            self.weight_bias = 0

        self.error = 0
        self.output = 0

    def classify(self, feature):
        return np.tanh(np.dot(feature, self.weights) + self.weight_bias)

    def get_decayed_error(self):
        if not hasattr(self, "decayed_error"):
            self.decayed_error = self.error * (1.0 - self.output * self.output)
        return self.decayed_error

class NNLayer():
    def __init__(self, node_num, feature_dim):
        self.nodes = [NNNode(feature_dim) for i in range(node_num)]
        self.feature_dim = feature_dim
        # self.errors = np.zeros(node_num)
        # self.outputs = np.zeros(node_num)

    def get_weights_to_backward(self, dim):
        return np.array([node.weights[dim] for node in self.nodes])
        
    def node_outputs_vector(self):
        # TODO numpy的にする
        return np.array([node.output for node in self.nodes])

class NNNetwork():
    def __init__(self, node_nums, first_feature_dim):
        self.layers = []
        for i, node_num in enumerate(node_nums):
            if i == 0:
                self.layers.append(
                    NNLayer(node_nums[i], first_feature_dim)
                )
            else:
                # 前のレイヤーのノード数がfeatureの次元数になる(バイアス除く)
                pre_node_num = node_nums[i-1]
                self.layers.append(
                    NNLayer(node_num, pre_node_num)
                )

    def forward(self, first_feature_vec):
        for i, layer in enumerate(self.layers):

            if i == 0:
                feature = first_feature_vec
            else:
                feature = np.array(self.layers[i-1].node_outputs_vector())

            for node in layer.nodes:
                node.output = node.classify(feature)  # TODO numpy的にする

    def error_backward(self, label):
        # TODO numpy的にする
        end_node = self.layers[-1].nodes[0]
        end_node.error = float(label) - end_node.output
        end_node.decayed_error = end_node.error * (1.0 - end_node.output * end_node.output)

        l = len(self.layers) - 2
        while l >= 0:
            for node_dim, node in enumerate(self.layers[l].nodes):
                decayed_error_vector = np.array(
                    [next_node.decayed_error for next_node in self.layers[l+1].nodes])

                weight_vector = np.array(
                    [next_node.weights[node_dim] for next_node in self.layers[l+1].nodes])

                node.error = np.dot(decayed_error_vector, weight_vector)
                node.decayed_error = node.error * (1.0 - node.output * node.output)

            l -= 1

    def update(self, first_feature_vec, learn_rate):
        for l, layer in enumerate(self.layers):
            if l == 0:
                input_vector = first_feature_vec
            else:
                input_vector = self.layers[l-1].node_outputs_vector()
                   
            for node in layer.nodes:
                node.weights = node.weights + learn_rate * node.decayed_error * input_vector 
                node.weight_bias = node.weight_bias + learn_rate * node.decayed_error

    def result_label(self):
        final_output = self.layers[-1].nodes[0].output
        if final_output >= 0:
            return 1
        else:
            return -1

    def final_error(self):
        return self.layers[-1].nodes[0].error


    def write_weight_ids(self, basefilename, ids):
        with open(basefilename+".ids", "w") as writer:
            for feature_id in sorted(ids.keys(), key=lambda k:ids[k]):
                dim = ids[feature_id]
                writer.write("%s\t%s\n" % (feature_id.encode("utf-8"), str(dim)))
        
        with open(basefilename+".weights", "w") as writer:
            for layer_id, layer in enumerate(self.layers):
                for node_id, node in enumerate(layer.nodes):
                    weight_list = ["%s:%s" % (str(wdim), str(weight)) 
                                   for wdim, weight in enumerate(node.weights)]
                    weight_str = "_".join(weight_list)
        
                    bias_str = "b:" + str(node.weight_bias)
                    writer.write("%s\t%s\t%s\t%s\n" % (
                        str(layer_id), str(node_id), bias_str, weight_str))

    @classmethod
    def read_nn_model(cls, filename, first_dim_num):
        # まずはレイヤー数、ノード数を知る
        with open(filename, "r") as f:
            layer_nodes = []
    
            pre_layer_id = -1
            for fline in f.readlines():
                # 入力は layeridの昇順, nodeidの昇順でソートされているものとする
                fline = unicode(fline, "utf-8")
                fline = fline.rstrip(u"\r\n")
                layer_id, node_id, bias_str, feature_str = fline.split(u"\t")
    
                layer_id = int(layer_id)
                node_id = int(node_id)
    
                if pre_layer_id != layer_id:
                    layer_nodes.append(0)
                layer_nodes[layer_id] = node_id + 1
                pre_layer_id = layer_id
    
        network = NNNetwork(layer_nodes, first_dim_num)
    
        # weightsを設定
        with open(filename, "r") as f:
            for fline in f.readlines():
                fline = unicode(fline, "utf-8")
                fline = fline.rstrip(u"\r\n")
                layer_id, node_id, bias_str, feature_str = fline.split(u"\t")
    
                layer_id = int(layer_id)
                node_id = int(node_id)
                b, bias = bias_str.split(":")
                bias = float(bias)
    
                if layer_id == 0:
                    vec = np.zeros(first_dim_num)
                else:
                    vec = np.zeros(layer_nodes[layer_id-1])
    
                for dim_value in feature_str.split(u"_"):
                    dim, value = dim_value.split(u":")
                    dim = int(dim)
                    value = float(value)
    
                    vec[dim] = value
                network.layers[layer_id].nodes[node_id].weights = vec
                network.layers[layer_id].nodes[node_id].weight_bias = bias
        return network

    @classmethod
    def read_ids(cls, filename):
        ids = {}
        with open(filename, "r") as f:
            for fline in f.readlines():
                fline = unicode(fline, "utf-8")
                fline = fline.rstrip(u"\r\n")
                feature_id, dim = fline.split(u"\t")
                dim = int(dim)
                ids[feature_id] = dim
        return ids
