# -*- coding: utf-8 -*-
from collections import defaultdict
class LinearClassifierDict(object):
    def __init__(self):
        self.weight = {}

    def classify(self, feature):
        ip = self.inner_prod_self(feature)
        if ip >= 0:
            return 1
        else:
            return -1

    def inner_prod_self(self, feature):
        return self.inner_prod(self.weight, feature)

    @classmethod
    def inner_prod(cls, feature_small, feature_large):
        ip = 0
        for feature_id, v_small in feature_small.iteritems():
            if feature_id in feature_large:
                v_large = feature_large[feature_id]
                ip += (v_small * v_large)
        return ip


    def read_weight_from_file(self, filename):
        with open(filename, "r") as reader:
            self.read_weight(reader)

    def read_weight(self, reader):
        weight = {}
        for line in reader.readlines():
            line = unicode(line, "utf-8")
            line = line.rstrip(u"\r\n")
            feature_id, value = line.split(u"\t")
                
            weight[feature_id] = float(value)
        self.weight = weight

    def write_weight_to_file(self, filename):
        with open(filename, "w") as writer:
            self.write_weight(writer)

    def write_weight(self, writer):
        for feature_id, value in self.weight.iteritems():
            if value == 0:
                continue
            writer.write("%s\t%s\n" % (feature_id.encode("utf-8"), str(value)))

    @classmethod    
    def get_feature(cls, **kwargs):
        feature = {}
        return feature

    def update_weight(self, **kwargs):
        pass

class Perceptron(LinearClassifierDict):
    def get_feature(self, words):
        feature = {}
        for word in words:
            feature_id = u"UNI:" + word
            if feature_id not in feature:
                feature[feature_id] = 0.0
            feature[feature_id] += 1.0
        return feature
    
    def update_weight(self, feature, label):
        for feature_id, value in feature.iteritems():
            if feature_id not in self.weight:
                self.weight[feature_id] = 0
            self.weight[feature_id] += label * value

class OnlineSVM(LinearClassifierDict):
    def __init__(self, c, margin):
        super(OnlineSVM, self).__init__()
        self.c = c
        self.margin = margin
        self.last = {}
        self.iteration = 0

    def inner_prod_self(self, feature):
        naiseki = sum( 
            [value * self.get_w(feature_id) for feature_id, value in feature.iteritems() ]
        )
    
        return naiseki
    
    def get_feature(self, words):
        feature = {}
        for word in words:
            feature_id = u"UNI:" + word
            if feature_id not in feature:
                feature[feature_id] = 0
            feature[feature_id] += 1
        return feature
    
    def get_w(self, feature_id):
        if feature_id not in self.last:
            self.weight[feature_id] = 0
            self.last[feature_id] = self.iteration
        elif self.iteration != self.last[feature_id]:
            c_size = self.c * (self.iteration - self.last[feature_id])
            if abs(self.weight[feature_id]) <= c_size:
                self.weight[feature_id] = 0
            else:
                sign_value = 1 if self.weight[feature_id] >= 0 else -1
                self.weight[feature_id] -= sign_value * c_size
            self.last[feature_id] = self.iteration
        return self.weight[feature_id]
    
    def update_weight(self, feature, label):
        self.iteration += 1
        for feature_id, value in feature.iteritems():
            current_weight = self.get_w(feature_id)
            self.weight[feature_id] = current_weight + label * value

    def write_weight(self, writer):
        for feature_id in self.weight.keys():
            value = self.get_w(feature_id)
            if value == 0:
                continue
            writer.write("%s\t%s\n" % (feature_id.encode("utf-8"), str(value)))

class OnlineSVMSimple(LinearClassifierDict):
    # OnlineSVMより遅いが、性能は同じ
    def __init__(self, c, margin):
        super(OnlineSVMSimple, self).__init__()
        self.c = c
        self.margin = margin

    def update_weight(self, feature, label):
        del_features = []
    
        for feature_id, value in self.weight.iteritems():
            if abs(value) <= self.c:
                del_features.append(feature_id)
            else:
                sign_value = 1 if value >= 0 else -1
                self.weight[feature_id] = value - (sign_value * self.c)
    
        for del_feature_id in del_features:
            del self.weight[del_feature_id]
    
        for feature_id, value in feature.iteritems():
            if feature_id not in self.weight:
                self.weight[feature_id] = 0
            self.weight[feature_id] += label * value


class StructuredPercepPosTagger(LinearClassifierDict):
    @classmethod
    def get_feature(cls, word, pos, pre_pos):
        feature = {}

        feature_id = u"PW:" + pos + u"_" + word
        feature[feature_id] = 1.0

        if pre_pos is not None:
            feature_id = u"PP:" + pre_pos + u"_" + pos
            feature[feature_id] = 1.0

        # 文頭の単語以外で大文字を含む、というfeature 
        if (pos != u"<s>") and (pos != u"</s>") and \
           (pre_pos != u"<s>") and any([char.isupper() for char in word]):
                feature_id = u"UP:" + pos
                feature[feature_id] = 1.0
        return feature


    def get_unknown_inner_prod(self, word, pos, pre_pos):
        # 高速化用
        if not hasattr(self, "ip_cache"):
            self.ip_cache = {}
        if not hasattr(self, "feature_cache"):
            self.feature_cache = {}

        if (word, pos, pre_pos) not in self.feature_cache:
            # 品詞-単語 のfeatureは weightには存在しないので除く
            all_feature = self.get_feature(word, pos, pre_pos)
            reduced_feature = dict([(feature_id, value) for feature_id, value in all_feature.iteritems()
                                    if feature_id[0:3] != "PW:"])

            # featureの情報をすべて持ったユニークキーを作る
            feature_cache_key = tuple(
                [(feature_id, reduced_feature[feature_id]) for feature_id in sorted(reduced_feature.keys())]
            )
            self.feature_cache[(word, pos, pre_pos)] = feature_cache_key

            if feature_cache_key not in self.ip_cache:
                self.ip_cache[feature_cache_key] = self.inner_prod_self(reduced_feature)

        feature_cache_key = self.feature_cache[(word, pos, pre_pos)]
        return self.ip_cache[feature_cache_key]


    @classmethod
    def get_sequence_feature(cls, words, poses):
        seq_feature = defaultdict(lambda: 0)

        for i in range(len(words)):
            word = words[i]
            pos = poses[i]
            pre_pos = poses[i-1] if i > 0 else None

            current_feature = cls.get_feature(word, pos, pre_pos)

            for feature_id, value in current_feature.iteritems():
                seq_feature[feature_id] += value

        return dict(seq_feature)


    def update_weight(self, correct_feature, best_feature):
        for feature_id, value in correct_feature.iteritems():
            if feature_id not in self.weight:
                self.weight[feature_id] = 0
            self.weight[feature_id] += value

        for feature_id, value in best_feature.iteritems():
            if feature_id not in self.weight:
                self.weight[feature_id] = 0
            self.weight[feature_id] -= value
