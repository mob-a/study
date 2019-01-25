# -*- coding: utf-8 -*-
import sys

from LinearClassifier import StructuredPercepPosTagger
from ViterbiGraph import NodeMap, PathMap, ViterbiGraph
#########################
def update_by_sentence(words, correct_poses, stp, normal_pos_list, exist_word_pos, exist_word):
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
    viterbigraph.set_start_node_id((u"<s>",0))
    viterbigraph.set_end_node_id((u"</s>",len(words)-1))
    viterbigraph.solve()

    # 最良の系列のfeatureを出す
    best_path  = viterbigraph.get_best_path()
    best_poses = [pos for pos, idx in best_path]
    best_feature = stp.get_sequence_feature(words, best_poses)
    
    # 正解系列のfeatureを出す
    correct_feature = stp.get_sequence_feature(words, correct_poses)

    # おもみ更新
    stp.update_weight(correct_feature, best_feature)
#########################

stp = StructuredPercepPosTagger()

# 全部の文を覚えておく
sentences = []
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    word_pos_list = [tuple(word_pos.split(u"_")) for word_pos in line.split(u" ")]
    words = [word for word, pos in word_pos_list]
    correct_poses = [pos for word, pos in word_pos_list]
    
    words.insert(0, u"<s>")
    words.append(u"</s>")

    correct_poses.insert(0, u"<s>")
    correct_poses.append(u"</s>")

    sentences.append((words, correct_poses))

# 品詞リスト出しとく
normal_poses = set()
for words, correct_poses in sentences:
    for pos in correct_poses:
        if pos not in [u"<s>", u"</s>"]:
            normal_poses.add(pos)
normal_pos_list = list(normal_poses)

# 既知の(品詞-単語)リストと既知の単語リストを出しておく
exist_word_pos = set()
exist_word = set()
for words, correct_poses in sentences:
    for i in range(len(words)):
        word = words[i]
        pos = correct_poses[i]
        exist_word_pos.add((word, pos))
        exist_word.add(word)

# 重み更新を繰り返す
iterate = int(sys.argv[1])
for it in range(iterate):
    for words, correct_poses in sentences:
        update_by_sentence(words, correct_poses, stp, normal_pos_list, exist_word_pos, exist_word)
stp.write_weight(sys.stdout)

with open(sys.argv[2], "w") as writer:
    for word, pos in sorted(list(exist_word_pos), key=lambda x:x[1]):
        writer.write("%s\t%s\n" %(word.encode("utf-8"), pos.encode("utf-8")))
