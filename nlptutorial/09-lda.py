# -*- coding: utf-8 -*-
import sys
import math
import numpy as np
from collections import defaultdict
from STOPWORDS import STOPWORDS
# 主にMURAWAKI Yugoさんの資料を参考にしている
# http://murawaki.org/misc/index.html

class Document():
    def __init__(self, topic_dim, words):
        word_num = len(words)

        self.word_num = word_num
        self.words = words

        # 初期トピックはランダムに割り当て
        self.topics = np.random.randint(0, topic_dim, word_num, 
                                        dtype="int64")

class LDA():
    def __init__(self, word_dim, topic_dim, words_list,
                 alpha_val, beta_val):

        self.topic_dim = topic_dim
        self.word_dim = word_dim

        # ハイパーパラメータ
        self.alpha = np.array([alpha_val] * topic_dim, 
                              dtype="float64")
        self.alpha_sum = np.sum(self.alpha)

        self.beta = np.array([beta_val] * word_dim, 
                             dtype="float64")
        self.beta_sum = np.sum(self.beta)

        # 文章のリスト
        self.documents = [Document(topic_dim, words) for words in words_list]
        self.document_num = len(self.documents)
   
        # 文書dにおけるトピックkの数をカウント
        self.n_jk = np.zeros((self.document_num, topic_dim), dtype="int64")
    
        # トピックkにおける語彙vの数をカウント
        self.n_kv = np.zeros((topic_dim, word_dim), dtype="int64")
    
        # トピックkにおける単語総数をカウント
        self.n_k = np.zeros(topic_dim, dtype="int64")
    
        # 各文書、各単語について、
        for j, document in enumerate(self.documents):
            for i in range(document.word_num):
                v = document.words[i]
                k = document.topics[i]
    
                self.n_jk[j][k] += 1
                self.n_kv[k][v] += 1
                self.n_k[k] += 1

    def sampling_iterate(self, iterate_num, probfile=None):
        for it in range(iterate_num):
            self.sampling_all_topics()

            if probfile is not None:
                log_prob = self.get_log_prob()
                probfile.write("iterate:%s log_prob:%s\n" % (str(it), str(log_prob)))

    def sampling_all_topics(self):
        # 各文書の各単語について
        for j, document in enumerate(self.documents):
            for di in range(document.word_num):
                v = document.words[di]
                old_k = document.topics[di]

                # 自身のカウントを減らす
                self.n_jk[j][old_k] -= 1
                self.n_kv[old_k][v] -= 1
                self.n_k[old_k] -= 1
                n_j = document.word_num - 1

                # 各トピックで、トピックの確率を求める
                topic_prob = np.array(
                    [self.topic_prob(di, j, kk, n_j=n_j) for kk in range(self.topic_dim)],
                    dtype="float64"
                )

                # 求めた確率に従い、一つランダムにトピックを選ぶ
                new_k = self.random_select_multi(topic_prob)

                # トピック更新
                document.topics[di] = new_k

                # カウントを増やす
                self.n_jk[j][new_k] += 1
                self.n_kv[new_k][v] += 1
                self.n_k[new_k] += 1

    def topic_prob(self, di, j, k, n_j=None):
        document = self.documents[j]
        v = document.words[di]

        numer1 = self.n_jk[j][k] + self.alpha[k]
        denom1 = n_j + self.alpha_sum

        numer2 = self.n_kv[k][v] + self.beta[v]
        denom2 = self.n_k[k] + self.beta_sum

        return (numer1 * numer2)/(denom1 * denom2);

    @staticmethod
    def random_select_multi(multi):
        dim = len(multi)
        # 一応、合計が1になっていない可能性も考慮しておく
        sum_prob = sum(multi)

        random_value = np.random.random()

        accumlation = 0
        for d in range(dim):
            accumlation += multi[d]

            if (accumlation / sum_prob)  >= random_value:
                return d

        # 実数演算の誤差で確率合計が乱数を超えない場合にも対応
        sys.stderr.write(
            "sampling error: %s / %s < %s\n" % (accumlation, sum_prob, random_value)
        )
        return np.random.randint(dim)

    def get_log_prob(self):
        log_prob = 0

        for j, document in enumerate(self.documents):
            n_j = document.word_num
            log_prob += math.lgamma(self.alpha_sum)
            log_prob -= math.lgamma(n_j + self.alpha_sum)

            for k in range(self.topic_dim):
                log_prob += math.lgamma(self.n_jk[j][k] + self.alpha[k])
                log_prob -= math.lgamma(self.alpha[k])
        
        for k in range(self.topic_dim):
            log_prob +=  math.lgamma(self.beta_sum)
            log_prob -= math.lgamma(self.n_k[k] + self.beta_sum)
            for v in range(self.word_dim):
                log_prob += math.lgamma(self.n_kv[k][v] + self.beta[v])
                log_prob -= math.lgamma(self.beta[v])
        return log_prob

    def best_topic(self, j):
        return np.argmax(
            np.array([self.n_jk[j][k] for k in range(self.topic_dim)])
        )


basefilename = sys.argv[3]

words_list = []
ids = defaultdict(lambda: len(ids))
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")

    words_list.append(
        np.array(
            [ids[word] for word in words if word not in STOPWORDS],
            dtype="int64"))

topic_num = int(sys.argv[1])
word_dim = len(ids)
alpha_val = 1.0
beta_val = 1.0
iterate_num = int(sys.argv[2])
lda = LDA(word_dim, topic_num, words_list, alpha_val, beta_val)
with open(basefilename + ".probs", "w") as pf:
    lda.sampling_iterate(iterate_num, probfile=pf)

best_topics = defaultdict(lambda :[])
for doc_id in range(len(words_list)):
    topic = lda.best_topic(doc_id)
    best_topics[topic].append(doc_id)

with open(basefilename + ".topics", "w") as tf:
    for t, docs in best_topics.iteritems():
        tf.write("%s\t%s\n" % (str(t), "_".join([str(d) for d in docs])))

with open(basefilename + ".topicwords", "w") as tf:
    for t, docs in best_topics.iteritems():
        tf.write("%s\t%s\n" % (str(t), "_".join([str(d) for d in docs])))
