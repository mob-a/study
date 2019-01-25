# -*- coding: utf-8 -*-

class HMM(object):
    def __init__(self, lambda_unigram=0.9, all_word_num=1):
        # 学習用
        self.pos_pos_counter = {}
        self.pos_word_counter = {}

        # テスト用
        self.pos_word_model = {}
        self.pos_pos_model = {}
        self.lambda_unigram = lambda_unigram
        self.all_word_num = all_word_num

    @staticmethod
    def increment_double_counter(counter, first, second):
        if first not in counter:
            counter[first] = {}
        if second not in counter[first]:
            counter[first][second] = 0
        counter[first][second] += 1

    
    @staticmethod
    def write_double_model(counter, model_type, writer):
        for first in sorted(counter.keys()):
            count_sum = sum(counter[first].values())
            for second in sorted(counter[first].keys()):
                count = counter[first][second]
                prob = 1.0 * count / count_sum
                writer.write("%s\t%s\t%s\t%s\n" % (model_type,
                                                   first.encode("utf-8"),
                                                   second.encode("utf-8"),
                                                   str(prob)))

    def write_model(self, writer):
        self.write_double_model(self.pos_pos_counter, "T", writer)
        self.write_double_model(self.pos_word_counter, "E", writer)
            
    def learn(self, word_pos_list, start_pos=None, end_pos=None):
        pre_pos = start_pos
        for word, pos in word_pos_list:
            # 品詞-単語
            self.increment_double_counter(self.pos_word_counter, pos, word)

            # 前品詞-後品詞. 最初の品詞の前は、Noneにするか、引数で指定できる
            if pre_pos is not None:
                self.increment_double_counter(self.pos_pos_counter, pre_pos, pos)
            pre_pos = pos

        # 最後の品詞の後は、Noneにするか、引数で指定できる
        if end_pos is not None:
            final_exist_pos = word_pos_list[-1][1]
            self.increment_double_counter(self.pos_pos_counter, final_exist_pos, end_pos)


    @staticmethod
    def set_double_model(model, first, second, prob):
        if first not in model:
            model[first] = {}
        model[first][second] = prob

    def read_model(self, filename):
        with open(filename, "r") as reader:
            for line in reader.readlines():
                line = unicode(line, "utf-8")
                line = line.rstrip(u"\r\n")
                model_type, first, second, prob = line.split(u"\t")
                if model_type == u"E":
                    self.set_double_model(self.pos_word_model, first, second, float(prob))
                elif model_type == u"T":
                    self.set_double_model(self.pos_pos_model, first, second, float(prob))
                else:
                    raise Exception

    def pos_pos_prob(self, pre_pos, current_pos):
        if current_pos not in self.pos_pos_model[pre_pos]:
            return 0
        return self.pos_pos_model[pre_pos][current_pos]
    
    def pos_word_prob(self, pos, word):
        word_prob = 0.0
        if word in self.pos_word_model[pos]:
            word_prob = self.pos_word_model[pos][word]
        prob = self.lambda_unigram * word_prob + (1-self.lambda_unigram) * (1.0/self.all_word_num)
    
        return prob
