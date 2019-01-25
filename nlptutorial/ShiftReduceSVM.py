# -*- coding: utf-8 -*-

from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from scipy import sparse
import numpy as np
from ShiftReduce import ShiftReduce
from collections import defaultdict

class ShiftReduceSVM(ShiftReduce):
    def __init__(self):
        super(ShiftReduceSVM, self).__init__()
        self.train_data_list = []
        self.train_labels = []

        # C = 1.0e5
        # kernel = "rbf"
        C = 1.0e10
        kernel = "poly"
        degree = 2
        gamma = "auto"
        self.featureid2dim = defaultdict(lambda: len(self.featureid2dim))
        self.estimator = SVC(C=C, kernel=kernel, degree=degree, probability=True, gamma=gamma)
        self.classifier = OneVsRestClassifier(self.estimator)

    def learn_classifier(self):
        # スパース行列 http://d.hatena.ne.jp/billest/20090906/1252269157
        # One Versus Rest のSVM http://qiita.com/sotetsuk/items/3a5718bb1f945a383ceb
        for fdict in self.train_data_list:
            for feature_id, value in fdict.iteritems():
                self.featureid2dim[feature_id]

        feature_dim = len(self.featureid2dim)
        xs = sparse.lil_matrix((len(self.train_data_list), feature_dim))
        for i, fdict in enumerate(self.train_data_list):
            for feature_id, value in fdict.iteritems():
                xs[i, self.featureid2dim[feature_id]] = value

        ys = np.array(self.train_labels, dtype="float64")
        self.classifier.fit(xs, ys)


    def shift_reduce_test(self):
        while (len(self.queue) > 0) or (len(self.stack) > 1):        
            ## 行動を決定
            vectors = self.to_vectors(self.make_feature())
            prob = self.classifier.predict_proba(vectors)
            
            s_shift = prob[0][self.SHIFT]
            s_lreduce = prob[0][self.LREDUCE]
            s_rreduce = prob[0][self.RREDUCE]

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

        
    def shift_reduce_train(self):
        while (len(self.queue) > 0) or (len(self.stack) > 1):
            corr = self.get_correct_action()
            action = corr

            self.train_data_list.append(self.make_feature())
            self.train_labels.append(corr)

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
    def shift_reduce_test(self):
        while (len(self.queue) > 0) or (len(self.stack) > 1):        
            ## 行動を決定
            vectors = self.to_vectors(self.make_feature())
            prob = self.classifier.predict_proba(vectors)
            
            s_shift = prob[0][self.SHIFT]
            s_lreduce = prob[0][self.LREDUCE]
            s_rreduce = prob[0][self.RREDUCE]

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

    def shift_reduce_train(self):
        while (len(self.queue) > 0) or (len(self.stack) > 1):
            corr = self.get_correct_action()
            action = corr

            self.train_data_list.append(self.make_feature())
            self.train_labels.append(corr)

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

    def to_vectors(self, feature):
        vec = np.zeros((1, len(self.featureid2dim)), dtype="float64")
        for feature_id, value in feature.iteritems():
            if feature_id in self.featureid2dim:
                vec[0][self.featureid2dim[feature_id]] = value
        return vec


    def make_feature(self):
        lw = self.left_word()
        lp = self.left_pos()
        rp = self.right_pos()
        rw = self.right_word()
        qw = self.queue_top_word()
        qp = self.queue_top_pos()

        feature_contains_none = [
            # self.feature_creator(u"LWRW", 1.0, [lw, rw]),
            # self.feature_creator(u"LWRP", 1.0, [lw, rp]),
            # self.feature_creator(u"LPRW", 1.0, [lp, rw]),
            # self.feature_creator(u"LPRP", 1.0, [lp, rp]),

            # self.feature_creator(u"LWQW", 1.0, [lw, qw]),
            # self.feature_creator(u"LWQP", 1.0, [lw, qp]),
            # self.feature_creator(u"LPQW", 1.0, [lp, qw]),
            # self.feature_creator(u"LPQP", 1.0, [lp, qp]),

            # self.feature_creator(u"RWQW", 1.0, [rw, qw]),
            # self.feature_creator(u"RWQP", 1.0, [rw, qp]),
            # self.feature_creator(u"RPQW", 1.0, [rp, qw]),
            # self.feature_creator(u"RPQP", 1.0, [rp, qp]),

            self.feature_creator(u"LW", 1.0, [lw]),
            self.feature_creator(u"LP", 1.0, [lp]),

            self.feature_creator(u"RW", 1.0, [rw]),
            self.feature_creator(u"RP", 1.0, [rp]),

            self.feature_creator(u"QP", 1.0, [qp]),
            self.feature_creator(u"QW", 1.0, [qw]),
        ]
    
        feature = dict(
            [f for f in feature_contains_none if (f is not None)]
        )
        return feature
