#!/bin/bash

set -eu
mkdir -p test

echo "# 00 #####################" && date
cat ../test/00-input.txt | python 00-intro.py > test/00-answer.txt
date

echo "# 01 #####################" && date
cat ../test/01-train-input.txt| python 01-unigram-train.py > test/01-sample-model.txt
cat ../test/01-test-input.txt| python 01-unigram-test.py test/01-sample-model.txt > test/01-sample-out.txt
date

echo "# 02 #####################" && date
cat ../data/wiki-en-train.word |  python 02-bigram-train.py > test/02-wikipedia-model.txt
cat ../data/wiki-en-test.word | python 02-bigram-test.py test/02-wikipedia-model.txt > test/02-wikipedia-entropy.txt
date

echo "# 03 #####################" && date
cat ../test/04-model.txt | perl -ple 's/^([^\t]+)\t([0-9\.]+)$/1\t$2\t$1/' > test/03-sample-mode.txt
cat ../test/04-input.txt | python 03-segmentation.py test/03-sample-mode.txt > test/03-sample-segments.txt

cat ../data/wiki-ja-train.word| python 01-unigram-train.py > test/03-wikipedia-unigram-model.txt
cat ../data/wiki-ja-test.txt | python 03-segmentation.py test/03-wikipedia-unigram-model.txt > test/03-wikipedia-segmentation.word
perl ../script/gradews.pl ../data/wiki-ja-test.word test/03-wikipedia-segmentation.word > test/03-accuracy.txt
date

echo "# 04 #####################" && date
cat ../test/05-train-input.txt | python 04-hmm-learn.py > test/04-hmm-sample-model.txt
cat ../test/05-test-input.txt |  python 04-hmm-test.py test/04-hmm-sample-model.txt > test/04-hmm-sample-answer.txt

cat ../data/wiki-en-train.norm_pos | python 04-hmm-learn.py > test/04-hmm-wikipedia-model.txt
cat ../data/wiki-en-test.norm | python 04-hmm-test.py test/04-hmm-wikipedia-model.txt > test/04-hmm-wikipedia-answer.pos
perl ../script/gradepos.pl ../data/wiki-en-test.pos test/04-hmm-wikipedia-answer.pos > test/04-accuracy.txt
date

echo "# 05 #####################" && date
cat ../test/03-train-input.txt| python 05-perceptron-train.py > test/05-sample-weight.txt

cat ../data/titles-en-train.labeled | python 05-perceptron-train.py > test/05-titles-weight.txt
cat ../data/titles-en-test.word | python 05-perceptron-test.py test/05-titles-weight.txt > test/05-test-titles.label
python ../script/grade-prediction.py ../data/titles-en-test.labeled test/05-test-titles.label > test/05-accuracy.txt
date


echo "# 06 #####################" && date
mkdir -p test/06

rm -f test/06/w*
cat ../data/titles-en-train.labeled | python 06-svm-train.py test/06/weight-titles
for w in test/06/weight-titles_*
do
    cat ../data/titles-en-test.word | python 05-perceptron-test.py $w > $w.label
    python ../script/grade-prediction.py ../data/titles-en-test.labeled $w.label > $w.accuracy
done
for f in test/06/*accuracy
do 
    echo $f
    cat $f
done > test/06/accuracy_list.txt
date


echo "# 07 #####################" && date
python 07-nn-sample.py > test/07-nn.txt

cat ../test/03-train-input.txt| python 07-nn-train.py test/07-nn-sample-train
echo -e "site Kyoto monk\nxyz born" | python 07-nn-test.py test/07-nn-sample-train.ids test/07-nn-sample-train.weights > test/07-nn-sample-test.txt

cat ../data/titles-en-train.labeled | python 07-nn-train.py test/07-nn-titles
cat ../data/titles-en-test.word | python 07-nn-test.py test/07-nn-titles.ids test/07-nn-titles.weights > test/07-titles.label
python ../script/grade-prediction.py ../data/titles-en-test.labeled test/07-titles.label > test/07-accuracy.txt
date


echo "# 08 #####################" && date
python 08-rnn-sample.py > test/08-rnn.txt

cat ../test/05-train-input.txt | python 08-rnn-train.py test/08-rnn-sample-model 200
cat ../test/05-test-input.txt | python 08-rnn-test.py test/08-rnn-sample-model > test/08-rnn-sample-test.txt

# # 非常に重い
# cat ../data/wiki-en-train.norm_pos | python 08-rnn-train.py test/08-wikipedia-pos-model 5
head -50 ../data/wiki-en-train.norm_pos | python 08-rnn-train.py test/08-wikipedia-pos-model 200
cat ../data/wiki-en-test.norm | python 08-rnn-test.py test/08-wikipedia-pos-model > test/08-wikipedia-test.pos
perl ../script/gradepos.pl ../data/wiki-en-test.pos test/08-wikipedia-test.pos > test/08-accuracy.txt
date

echo "# 09 #####################" && date
cat ../test/07-train.txt | python 09-lda.py 2 1000 test/09-lda-sample
cat ../test/07-train.txt | python 09-view-cluster.py test/09-lda-sample.topics > test/09-sample.words

# # 非常に重い
# cat ../data/wiki-en-documents.word | python 09-lda.py 3 50 test/09-lda-wikipedia
cat ../data/wiki-en-documents.word | python 09-lda.py 3 10 test/09-lda-wikipedia
cat ../data/wiki-en-documents.word | python 09-view-cluster.py test/09-lda-wikipedia.topics > test/09-wikipedia.words
date

echo "# 10 #####################" && date

cat ../test/08-input.txt | python 10-cky.py ../test/08-grammar.txt > test/10-sample-phrase.txt
cat ../data/wiki-en-short.tok | python 10-cky.py ../data/wiki-en-test.grammar > test/10-wikipedia-phrase.txt
# # # GUIがないと動かない?
# # # cat test/10wikipedia.tree | python ../script/print-trees.py 
date

echo "# 11 #####################" && date
cat ../data/mstparser-en-train.dep | python 11-train-sr.py test/11-sr-mst.weight
cat ../data/mstparser-en-test.dep | python 11-test-sr.py test/11-sr-mst.weight > test/11-sr-mst.dep
python ../script/grade-dep.py ../data/mstparser-en-test.dep test/11-sr-mst.dep > test/11-accracy.txt

cat ../data/mstparser-en-train.dep | python 11-train-sr-avg.py test/11-sr-mst-avg.weight
cat ../data/mstparser-en-test.dep | python 11-test-sr.py test/11-sr-mst-avg.weight > test/11-sr-mst-avg.dep
python ../script/grade-dep.py ../data/mstparser-en-test.dep test/11-sr-mst-avg.dep > test/11-accracy-avg.txt

# # sklearnが必要
python 11-sr-svm.py ../data/mstparser-en-train.dep ../data/mstparser-en-test.dep > test/11-sr-mst-svm.dep
python ../script/grade-dep.py ../data/mstparser-en-test.dep  test/11-sr-mst-svm.dep > test/11-accracy-svm.txt
date


echo "# 12 #####################" && date

cat ../test/05-train-input.txt | python 12-train-hmm-percep.py 10 test/12-sample-train.word_pos > test/12-sample-train.weight
cat ../test/05-test-input.txt | python 12-test-hmm-percep.py test/12-sample-train.weight test/12-sample-train.word_pos > test/12-sample-test.txt

# # 非常に重い
cat ../data/wiki-en-train.norm_pos | python 12-train-hmm-percep.py 1 test/12-wikipedia-train.word_pos > test/12-wikipedia-train.weight
cat ../data/wiki-en-test.norm | python 12-test-hmm-percep.py test/12-wikipedia-train.weight test/12-wikipedia-train.word_pos > test/12-wikipedia-test.pos
perl ../script/gradepos.pl ../data/wiki-en-test.pos test/12-wikipedia-test.pos > test/12-accuracy.txt

date

echo "# 13 #####################" && date
date > test/13-accuracy.1.txt
cat ../data/wiki-en-test.norm | python 13-beam-hmm.py test/04-hmm-wikipedia-model.txt 1 > test/13-wikipedia-test.1.pos
perl ../script/gradepos.pl ../data/wiki-en-test.pos test/13-wikipedia-test.1.pos >> test/13-accuracy.1.txt
date >> test/13-accuracy.1.txt

date > test/13-accuracy.3.txt
cat ../data/wiki-en-test.norm | python 13-beam-hmm.py test/04-hmm-wikipedia-model.txt 3 > test/13-wikipedia-test.3.pos
perl ../script/gradepos.pl ../data/wiki-en-test.pos test/13-wikipedia-test.3.pos >> test/13-accuracy.3.txt
date >> test/13-accuracy.3.txt

date > test/13-accuracy.10.txt
cat ../data/wiki-en-test.norm | python 13-beam-hmm.py test/04-hmm-wikipedia-model.txt 10 > test/13-wikipedia-test.10.pos
perl ../script/gradepos.pl ../data/wiki-en-test.pos test/13-wikipedia-test.10.pos >> test/13-accuracy.10.txt
date >> test/13-accuracy.10.txt

date > test/13-accuracy.100.txt
cat ../data/wiki-en-test.norm | python 13-beam-hmm.py test/04-hmm-wikipedia-model.txt 100 > test/13-wikipedia-test.100.pos
perl ../script/gradepos.pl ../data/wiki-en-test.pos test/13-wikipedia-test.100.pos >> test/13-accuracy.100.txt
date >> test/13-accuracy.100.txt

date
