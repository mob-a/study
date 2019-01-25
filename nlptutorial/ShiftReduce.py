# -*- coding: utf-8 -*-

from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from scipy import sparse
import numpy as np

class SRNode(object):
    def __init__(self, node_id, word, pos):
        self.id = node_id
        self.word = word
        self.pos = pos
        self.head = -1

        # 学習時のみ使う
        self.unproc = 0
        self.correct_head = -1

class ShiftReduce(object):
    SHIFT = 0
    LREDUCE = 1
    RREDUCE = 2

    def __init__(self):
        self.w_shift = {}
        self.w_lreduce = {}
        self.w_rreduce = {}

    def initialize(self, word_pos_list, train_flag=False, correct_heads={}):
        self.stack = [SRNode(0, u"ROOT", u"ROOT")]
        self.queue = [SRNode(i+1, word_pos[0], word_pos[1])
                      for i ,word_pos in enumerate(word_pos_list)]

        self.nodeid2node = dict()
        self.nodeid2node[0] = self.stack[0]
        for node in self.queue:
            self.nodeid2node[node.id] = node

        if train_flag and correct_heads:
            # 学習用設定
            self.train_flag = True

            # 正解headを設定
            for node in self.queue:
                node.correct_head = correct_heads[node.id]

            # unprocを設定
            for head_node_id in correct_heads.values():
                self.nodeid2node[head_node_id].unproc += 1
        else:
            self.train_flag = False

    def shift_reduce(self):
        while (len(self.queue) > 0) or (len(self.stack) > 1):        
            ## 各行動のスコアを計算
            feature = self.make_feature()

            s_shift = self.inner_prod(self.w_shift, feature, normalize=False)
            s_lreduce = self.inner_prod(self.w_lreduce, feature, normalize=False)
            s_rreduce = self.inner_prod(self.w_rreduce, feature, normalize=False)

            ## 行動を選択
            if len(self.queue) <= 0:
                if s_lreduce >= s_rreduce:
                    action = self.LREDUCE
                else:
                    action = self.RREDUCE
            elif len(self.stack) <= 1:
                action = self.SHIFT
            elif (s_shift >= s_lreduce) and (s_shift >= s_rreduce):
                action = self.SHIFT
            elif (s_lreduce >= s_shift) and (s_lreduce >= s_rreduce):
                action = self.LREDUCE
            elif (s_rreduce >= s_shift) and (s_rreduce >= s_lreduce):
                action = self.RREDUCE
            else:
                raise Exception

            ## 学習モードの場合、重みを学習する. 行動は正しいものに修正
            if self.train_flag:
                corr = self.get_correct_action()
                self.train(action, corr, feature)
                action = corr

            ## 行動実行
            if action == self.SHIFT:
                val = self.queue.pop(0)
                self.stack.append(val)
            elif action == self.LREDUCE:
                right = self.stack.pop()
                left =  self.stack.pop()        
                left.head = right.id
                self.stack.append(right)
            elif action == self.RREDUCE:
                right = self.stack.pop()
                left =  self.stack.pop()    
                right.head = left.id
                self.stack.append(left)
            else:
                raise Exception

    def get_correct_action(self):
        # 資料18ページがなんか違う気がする
        if len(self.stack) >= 2:
            left = self.stack[-2]
            right = self.stack[-1]
            if (right.correct_head == left.id) and (right.unproc == 0):
                corr = self.RREDUCE
                left.unproc -= 1
            elif (left.correct_head == right.id) and (left.unproc == 0):
                corr = self.LREDUCE
                right.unproc -= 1
            else:
                corr = self.SHIFT
        else:
            corr = self.SHIFT
        return corr

    def train(self, action, corr, feature):
        if action != corr:
            if action == self.SHIFT:
                minus_target = self.w_shift
            elif action == self.LREDUCE:
                minus_target = self.w_lreduce
            elif action == self.RREDUCE:
                minus_target = self.w_rreduce

            if corr == self.SHIFT:
                plus_target = self.w_shift
            elif corr == self.LREDUCE:
                plus_target = self.w_lreduce
            elif corr == self.RREDUCE:
                plus_target = self.w_rreduce
                
            for feature_id, val in feature.iteritems():
                if feature_id not in minus_target:
                    minus_target[feature_id] = 0
                if feature_id not in plus_target:
                    plus_target[feature_id] = 0

                minus_target[feature_id] -= val
                plus_target[feature_id] += val

    def make_feature(self):
        lw = self.left_word()
        lp = self.left_pos()
        rp = self.right_pos()
        rw = self.right_word()
        qw = self.queue_top_word()
        qp = self.queue_top_pos()

        feature_contains_none = [
            self.feature_creator(u"LWRW", 1.0, [lw, rw]),
            self.feature_creator(u"LWRP", 1.0, [lw, rp]),
            self.feature_creator(u"LPRW", 1.0, [lp, rw]),
            self.feature_creator(u"LPRP", 1.0, [lp, rp]),

            self.feature_creator(u"LWQW", 1.0, [lw, qw]),
            self.feature_creator(u"LWQP", 1.0, [lw, qp]),
            self.feature_creator(u"LPQW", 1.0, [lp, qw]),
            self.feature_creator(u"LPQP", 1.0, [lp, qp]),

            self.feature_creator(u"RWQW", 1.0, [rw, qw]),
            self.feature_creator(u"RWQP", 1.0, [rw, qp]),
            self.feature_creator(u"RPQW", 1.0, [rp, qw]),
            self.feature_creator(u"RPQP", 1.0, [rp, qp]),

            self.feature_creator(u"LW", 1.0, [lw]),
            self.feature_creator(u"LP", 1.0, [lp]),

            self.feature_creator(u"RW", 1.0, [rw]),
            self.feature_creator(u"RP", 1.0, [rp]),

            self.feature_creator(u"QW", 1.0, [qw]),
            self.feature_creator(u"QP", 1.0, [qp]),
        ]
    
        feature = dict(
            [f for f in feature_contains_none if (f is not None)]
        )
        return feature

    def feature_creator(self, prefix, value, fstrs):
        for fstr in fstrs:
            if fstr is None:
                return None

        feature_id = prefix + u"_" + u"_".join(fstrs)
        return (feature_id, value)

    def left_word(self):
        if len(self.stack) >= 2:
            return self.stack[-2].word
        else:
            return None

    def left_pos(self):
        if len(self.stack) >= 2:
            return self.stack[-2].pos
        else:
            return None
        
    def right_word(self):
        if len(self.stack) >= 1:
            return self.stack[-1].word
        else:
            return None

    def right_pos(self):
        if len(self.stack) >= 1:
            return self.stack[-1].pos
        else:
            return None

    def queue_top_word(self):
        if len(self.queue) >= 1:
            return self.queue[0].word
        else:
            return None

    def queue_top_pos(self):
        if len(self.queue) >= 1:
            return self.queue[0].pos
        else:
            return None

    @staticmethod
    def inner_prod(feature_large, feature_small, normalize=True):
        ip = 0
        for k, v_small in feature_small.iteritems():
            if k in feature_large:
                v_large = feature_large[k]
                ip += (v_small * v_large)
        
        if normalize:
            norm2_small = 0
            for v in feature_small.values():
                norm2_small += (v * v)

            norm2_large = 0
            for v in feature_large.values():
                norm2_large += (v * v)

            ip = ip / math.sqrt(norm2_small * norm2_large)
            
        return ip

    def write_weight(self, filename):
        weights = [(self.w_shift, "SH"), (self.w_lreduce, "LR"), (self.w_rreduce, "RR")]
                
        with open(filename, "w") as writer:
            for weight, weight_id in weights:
                for feature_id in sorted(weight.keys()):
                    value = weight[feature_id]
                    writer.write("%s\t%s\t%s\n" % (weight_id,
                                                   feature_id.encode("utf-8"),
                                                   str(value)))

    def read_weight(self, filename):
        with open(filename, "r") as reader:
            for line in reader.readlines():
                line = unicode(line, "utf-8")
                line = line.rstrip(u"\r\n")
                weight_id, feature_id, value = line.split(u"\t")
                if weight_id == u"SH":
                    self.w_shift[feature_id] = float(value)
                elif weight_id == u"LR":
                    self.w_lreduce[feature_id] = float(value)
                elif weight_id == u"RR":
                    self.w_rreduce[feature_id] = float(value)
                else:
                    raise Exception

    def write_tree(self, writer, all_data_list):
        for dat_tuple in all_data_list:
            node_id = int(dat_tuple[0])
            result_tuple = dat_tuple + (unicode(self.nodeid2node[node_id].head), u"<UNDEF>")
            result_str = u"%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % result_tuple
            writer.write(result_str.encode("utf-8"))
        writer.write("\n")



class ShiftReduceAvg(ShiftReduce):
    def __init__(self):
        super(ShiftReduceAvg, self).__init__()
        self.wa_shift = {}
        self.wa_lreduce = {}
        self.wa_rreduce = {}
        self.t_shift = 1
        self.t_lreduce = 1
        self.t_rreduce = 1

    def train(self, action, corr, feature):
        # Averaged Perceptronにしてみる 
        # http://www.ss.cs.tut.ac.jp/nlp2011/nlp2010_tutorial_okanohara.pdf
        if action != corr:
            if action == self.SHIFT:
                minus_target = self.w_shift
                minus_target_a = self.wa_shift
                minus_t = self.t_shift
                self.t_shift += 1
            elif action == self.LREDUCE:
                minus_target = self.w_lreduce
                minus_target_a = self.wa_lreduce
                minus_t = self.t_lreduce
                self.t_lreduce += 1
            elif action == self.RREDUCE:
                minus_target = self.w_rreduce
                minus_target_a = self.wa_rreduce
                minus_t = self.t_rreduce
                self.t_rreduce += 1
            self.update_weight(minus_target, feature, -1, minus_t, minus_target_a)

            if corr == self.SHIFT:
                plus_target = self.w_shift
                plus_target_a = self.wa_shift
                plus_t = self.t_shift
                self.t_shift += 1
            elif corr == self.LREDUCE:
                plus_target = self.w_lreduce
                plus_target_a = self.wa_lreduce
                plus_t = self.t_lreduce
                self.t_lreduce += 1
            elif corr == self.RREDUCE:
                plus_target = self.w_rreduce
                plus_target_a = self.wa_rreduce
                plus_t = self.t_rreduce
                self.t_rreduce += 1
            self.update_weight(plus_target, feature, 1, plus_t, plus_target_a)

    @staticmethod
    def update_weight(weight, feature, label, t, weight_a):
        for feature_id, value in feature.iteritems():
            if feature_id not in weight:
                weight[feature_id] = 0
            weight[feature_id] += label * value

            if feature_id not in weight_a:
                weight_a[feature_id] = 0
            weight_a[feature_id] += t * label * value

    def weight_average(self):
        self._minus_weight(self.w_shift, self.wa_shift, self.t_shift)
        self._minus_weight(self.w_lreduce, self.wa_lreduce, self.t_lreduce)
        self._minus_weight(self.w_rreduce, self.wa_rreduce, self.t_rreduce)

    @staticmethod
    def _minus_weight(base, target, t):
        for fid in base.keys():
            base[fid] = base[fid] - (1.0 * target[fid] / t)


