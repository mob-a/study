# -*- coding: utf-8 -*-
from collections import Counter
import math
class Ngram(object):
    def __init__(self, max_n, all_word_num=1, lambda_unigram=0.9, lambda_ngram=0.9):
        self.max_n = max_n
        # 学習用
        ngram_counter = {}
        for n in range(1, max_n+1):
            ngram_counter[n] = Counter()
        self.ngram_counter = ngram_counter

        # テスト用
        ngram_model = {}
        for n in range(1, max_n+1):
            ngram_model[n] = {}        
        self.ngram_model = ngram_model
        self.all_word_num = all_word_num
        self.lambda_unigram = lambda_unigram
        self.lambda_ngram = lambda_ngram


    def learn(self, words):
        for i in range(len(words)):
            for n in range(1, self.max_n+1):
                ngram = self.get_ngram(n, i, words)
                if ngram is not None:
                    self.ngram_counter[n][ngram] += 1

    def get_ngram(self, n, idx, words):
        if idx-n+1 >= 0:
            return tuple(words[idx-n+1:idx+1])
        else:
            return None

    def all_unigram_count(self):
        return sum(self.ngram_counter[1].values())

    def write_model(self, writer):
        for n in range(1, self.max_n+1):
            all_unigram_count = self.all_unigram_count()
            for ngram, count in self.ngram_counter[n].iteritems():
                if n == 1:
                    prob = 1.0 * count / all_unigram_count
                else:
                    pre_count = self.ngram_counter[n-1][ngram[0:n-1]]
                    prob = 1.0 * count / pre_count
        
                ngram_str = u"\t".join(ngram)
                writer.write("%s\t%s\t%s\n" % (
                    str(n), str(prob), ngram_str.encode("utf-8")))

    def write_model_to_file(self, filename):
        with open(filename, "w") as writer:
            self.write_model(writer)

       
    def read_model(self, reader):
        for line in reader.readlines():
            line = unicode(line, "utf-8")
            line = line.rstrip(u"\r\n")
            n_prob_ngram = line.split(u"\t")
            
            n = int(n_prob_ngram[0])
            prob = float(n_prob_ngram[1])
            ngram = tuple(n_prob_ngram[2:])
                
            self.ngram_model[n][ngram] = prob
    
    def read_model_from_file(self, filename):
        with open(filename, "r") as reader:
            self.read_model(reader)

    def get_sentence_prob(self, words):
        log_prob = 0
        for i in xrange(len(words)):
            ngram = self.get_ngram(self.max_n, i, words)
            word = words[i]

            if ngram is None:
                continue # TODO: とりあえず

            if self.max_n == 1:
                prob = self.get_unigram_prob(word)
            else:
                prob = self.get_ngram_prob(ngram, word)
            log_prob = log_prob + math.log(prob, 2.0)
        return log_prob
    
    def get_unigram_prob(self, word):
        word_tuple = (word, )
        if word_tuple in self.ngram_model[1]:
            prob = self.lambda_unigram * self.ngram_model[1][word_tuple] + (1.0 - self.lambda_unigram) * (1.0/self.all_word_num)
        else:
            prob = (1.0 - self.lambda_unigram) * (1.0/self.all_word_num)
        return prob 

    def get_ngram_prob(self, ngram, word):
        unigram_prob = self.get_unigram_prob(word)
        n = len(ngram)
        if ngram in self.ngram_model[n]:
            prob = self.lambda_ngram * self.ngram_model[n][ngram] + (1.0 - self.lambda_ngram) * unigram_prob
        else:
            prob = (1.0 - self.lambda_ngram) * unigram_prob
        return prob 

    def covered(self, words):
        covered = 0

        n = self.max_n
        for i in xrange(len(words)):
            ngram = self.get_ngram(n, i, words)

            if (ngram is not None) and (ngram in self.ngram_model[n]):
                covered += 1
        return covered
