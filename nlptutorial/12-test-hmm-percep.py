# -*- coding: utf-8 -*-
import sys
from LinearClassifier import StructuredPercepPosTagger
from ViterbiGraph import NodeMap, PathMap, ViterbiGraph

#########################
def get_best_poses(words, stp, normal_pos_list, exist_word_pos, exist_word):
    LARGE_SCORE = 1.0e10

    # ビタビ用のグラフ作成
    # ノードマップの初期化
    nodemap = NodeMap()
    for i in range(len(words)):
        # 先頭は 品詞 <s> のみ.
        # 2番目～最後の1つ前までは、全品詞
        # 最後は、品詞 </s> のみ.
        # node_id は (品詞, point)のtupleとしておく
        if i == 0:
            nodemap.set_node((u"<s>", i), i, min_score=0)
        elif i < len(words) - 1:
            for pos in normal_pos_list:
                nodemap.set_node((pos, i), i)
        else:
            nodemap.set_node((u"</s>", i), i)

    # パスマップの初期化
    pathmap = PathMap()
    for i ,word in enumerate(words):
        if i == 0:
            continue

        nodes = nodemap.get_node_ids_by_point(i)
        pre_nodes = nodemap.get_node_ids_by_point(i - 1)
        for node_id in nodes:
            current_pos = node_id[0]

            # とてつもなく候補数が多く遅いので、
            # featureを使うのは学習データに存在する(品詞-単語)だけにする.
            # ただし、未知の単語はあらゆる品詞でfeatureを出す
            for pre_node_id in pre_nodes:
                if (word,current_pos) in exist_word_pos:
                    pre_pos = pre_node_id[0]
    
                    # 単語,現ノードのpos,前ノードのposごとに異なるfeatureを作る
                    # スコアは、featureとweightの内積*-1.0(スコア最小のパスを出すため)
                    feature = stp.get_feature(word, current_pos, pre_pos)
                    score = -1.0 * stp.inner_prod_self(feature)
                elif word not in exist_word:
                    # キャッシュ使う
                    pre_pos = pre_node_id[0]
                    score = -1.0 * stp.get_unknown_inner_prod(word, current_pos, pre_pos)
                else:
                    score = LARGE_SCORE
                pathmap.set_path(pre_node_id, node_id, score)

    viterbigraph = ViterbiGraph(nodemap, pathmap)
    viterbigraph.set_start_node_id((u"<s>", 0))
    viterbigraph.set_end_node_id((u"</s>", len(words)-1))
    viterbigraph.solve()

    best_path =  viterbigraph.get_best_path()
    return [pos for pos, idx in best_path]
#########################

stp = StructuredPercepPosTagger()
stp.read_weight_from_file(sys.argv[1])

# 品詞リストを出しとく
all_poses = set()
for feature_id in stp.weight.keys():
    if feature_id[0:3] == u"PP:":
        pre_pos, current_pos = feature_id[3:].split(u"_")
        all_poses.add(pre_pos)
        all_poses.add(current_pos)
normal_pos_list = [pos for pos in all_poses if pos not in [u"<s>", u"</s>"]]

# 既知の(品詞-単語)リストと既知の単語リストを読んでおく
exist_word_pos = set()
exist_word = set()
with open(sys.argv[2], "r") as reader:
    for fline in reader.readlines():
        fline = unicode(fline, "utf-8")
        fline = fline.rstrip(u"\r\n")
        word, pos = fline.split(u"\t")

        exist_word_pos.add((word, pos))
        exist_word.add(word)

# 各文で、最良の品詞リストを出す
sentence_list = []
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")
    
    words.insert(0, u"<S>")
    words.append(u"</S>")
    sentence_list.append(words)

for i, words in enumerate(sentence_list):
    best_poses = get_best_poses(words, stp, normal_pos_list, exist_word_pos, exist_word)
    print u" ".join(best_poses[1:-1]).encode("utf-8")
