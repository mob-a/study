# -*- coding: utf-8 -*-

import numpy as np

class RNNHiddenNode():
    def __init__(self, feature_dim, hidden_node_num):
        self.weights = (np.random.rand(feature_dim) - 0.5) * 0.2
        self.bias = (np.random.rand() - 0.5) * 0.2
        self.weights_memory = (np.random.rand(hidden_node_num) - 0.5) * 0.2

        self.outputs = []

    def classify(self, feature, prev_outputs):
        output = np.tanh(
            np.dot(feature, self.weights) + \
            np.dot(prev_outputs, self.weights_memory) + \
            self.bias
        )
        return output

class RNNOutputNode():
    def __init__(self, hidden_node_num):
        self.weights = (np.random.rand(hidden_node_num) - 0.5) * 0.2
        self.bias = (np.random.rand() - 0.5) * 0.2

        self.probs = []

class RNNNetwork():
    def __init__(self, feature_dim, class_num, hidden_node_num):
        self.output_nodes = [
            RNNOutputNode(hidden_node_num) for c in range(class_num)]
        self.hidden_nodes = [
            RNNHiddenNode(feature_dim, hidden_node_num) for i in range(hidden_node_num)]
        self.class_outputs = []

        self.forget()

    def forget(self):
        self.class_outputs = []
        for output_node in self.output_nodes:
            output_node.probs = []
        for hidden_node in self.hidden_nodes:
            hidden_node.outputs = []
        
        self.cached_hidden_out = {}
        self.cached_class_prob = {}
        self.cached_output_weight = {}

    def get_hidden_node_num(self):
        return len(self.hidden_nodes)

    def get_class_num(self):
        return len(self.output_nodes)

    def get_cached_hidden_out(self, t):
        if t not in self.cached_hidden_out:
            self.cached_hidden_out[t] = np.array(
                [hidden_node.outputs[t] for hidden_node in self.hidden_nodes])
        return self.cached_hidden_out[t]

    def get_cached_class_prob(self, t):
        if t not in self.cached_class_prob:
            self.cached_class_prob[t] = np.array(
                [output_node.probs[t] for output_node in self.output_nodes])
        return self.cached_class_prob[t]

    def get_cached_output_weight(self, h):
        if h not in self.cached_output_weight:
            self.cached_output_weight[h] = np.array(
                [output_node.weights[h] for output_node in self.output_nodes])
        return self.cached_output_weight[h]
        
    @staticmethod
    def find_max(class_prob):
        max_prob = class_prob[0]
        max_class = 0
        for c in range(1, len(class_prob)):
            if max_prob < class_prob[c]:
                max_prob = class_prob[c]
                max_class = c
        return max_class

                
    def get_class_prob(self, feature):
        class_num = self.get_class_num()
        class_values = np.zeros(class_num)
        for c in range(class_num):
            output = np.exp(
                np.dot(feature, self.output_nodes[c].weights) + self.output_nodes[c].bias
            )
            class_values[c] = output
        class_prob = class_values / np.sum(class_values)
        return class_prob

    def forward(self, time_feature_vec):
        class_num = self.get_class_num()
        for t, feature_vec in enumerate(time_feature_vec):
            if t == 0:
                prev_outputs = np.zeros(len(self.hidden_nodes))
            else:
                prev_outputs = self.get_cached_hidden_out(t-1)

            # h[t] を設定
            for hidden_node in self.hidden_nodes:
                output = hidden_node.classify(feature_vec, prev_outputs)
                hidden_node.outputs.append(output)
            hidden_out = self.get_cached_hidden_out(t)

            # p[t] を設定
            class_prob = self.get_class_prob(hidden_out)
            for c in range(class_num):
                self.output_nodes[c].probs.append(class_prob[c])

            # y[t]を設定
            y = self.find_max(class_prob)
            self.class_outputs.append(y)

    def onehot(self, dim, dim_num):
        oh = np.zeros(dim_num)
        oh[dim] = 1.0
        return oh

    def gradient(self, collect_ys, time_feature_vec, feature_dim):
        time_end = len(collect_ys)
        class_num = self.get_class_num()
        hidden_node_num = self.get_hidden_node_num()

        # 勾配初期化
        delta_output_weights = np.zeros((class_num, hidden_node_num))
        delta_output_bias = np.zeros(class_num)
        delta_hidden_weights = np.zeros((hidden_node_num, feature_dim))
        delta_hidden_weights_memory = np.zeros((hidden_node_num, hidden_node_num))
        delta_hidden_bias = np.zeros(hidden_node_num)

        post_error_hiddens = np.zeros(hidden_node_num)        
        for t in reversed(range(time_end)):
            onehot = self.onehot(collect_ys[t], class_num)
            class_prob = self.get_cached_class_prob(t)
            hidden_out = self.get_cached_hidden_out(t)
            if t != 0:
                prev_hidden_out = self.get_cached_hidden_out(t-1)

            # 出力層のweightとbias更新
            error_output_by_class = onehot - class_prob            

            for c in range(class_num):
                delta_output_weights[c] += error_output_by_class[c] * hidden_out
                delta_output_bias[c] += error_output_by_class[c]

            error_hidden_dashes = np.zeros(hidden_node_num)
            for h, hidden_node in enumerate(self.hidden_nodes):
                # 誤差の逆伝搬
                weights_to_output = self.get_cached_output_weight(h)
                error_hidden = np.dot(post_error_hiddens, hidden_node.weights_memory) + \
                               np.dot(error_output_by_class, weights_to_output)
                # tanhの勾配
                error_hidden_dashes[h] = error_hidden * (1.0 - hidden_node.outputs[t]**2.0)
                error_hidden_dash = error_hidden_dashes[h] 

                # 隠れ層のweightとbias更新
                delta_hidden_weights[h] += error_hidden_dash * time_feature_vec[t]
                delta_hidden_bias[h] += error_hidden_dash
                if t != 0:
                    delta_hidden_weights_memory[h] += np.dot(error_hidden_dash, prev_hidden_out)

            # 前の時間に勾配を渡す
            post_error_hiddens = error_hidden_dashes

        return  (delta_output_weights,
                 delta_output_bias,
                 delta_hidden_weights,
                 delta_hidden_weights_memory,
                 delta_hidden_bias)

    def update_weight(self, 
                      learn_rate,
                      delta_output_weights,
                      delta_output_bias,
                      delta_hidden_weights,
                      delta_hidden_weights_memory,
                      delta_hidden_bias):

        for c in range(self.get_class_num()):
            self.output_nodes[c].weights += learn_rate * delta_output_weights[c]
            self.output_nodes[c].bias += learn_rate * delta_output_bias[c]

        for h in range(self.get_hidden_node_num()):
            self.hidden_nodes[h].weights += learn_rate * delta_hidden_weights[h]
            self.hidden_nodes[h].weights_memory += learn_rate * delta_hidden_weights_memory[h]
            self.hidden_nodes[h].bias += learn_rate * delta_hidden_bias[h]

