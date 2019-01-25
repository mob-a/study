# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
import math
from ViterbiGraph import NodeMap, PathMap, BeamGraph
from HMM import HMM

LARGE_SCORE = 10.0**10

def get_best_poses(words, normal_pos_list, hmm, beam_width):
    # ビームサーチ用のグラフ作成
    beam_graph = BeamGraph(NodeMap(), PathMap(), beam_width)
    for i, word in enumerate(words):
        # 先頭は 品詞 <s> のみ.
        # 2番目～最後の1つ前までは、全品詞
        # 最後は、品詞 </s> のみ.
        # node_id は (品詞, point)のtupleとしておく
        if i == 0:
            node_id = (u"<s>", i)
            beam_graph.node_map.set_node(node_id, i, min_score=0)
            beam_graph.set_start_node_id(node_id)

        elif i < len(words) - 1:
            pre_nodes = beam_graph.node_map.get_node_ids_by_point(i-1)

            # このポイントにposごとにノードを作り、前のポイントのノードリストの間にパスを張る
            for pos in normal_pos_list:
                node_id = (pos, i)
                beam_graph.node_map.set_node(node_id, i)

                if i == len(words) - 1:
                    # 最後の品詞</s>は品詞-単語確率1.0としておく
                    pwp = 1.0
                else:
                    pwp = hmm.pos_word_prob(pos, word)
        
                for pre_node_id in pre_nodes:
                    pre_pos = pre_node_id[0]
                    prob = hmm.pos_pos_prob(pre_pos, pos) * pwp
    
                    if prob > 0:
                        score = -1.0 * math.log(prob, 2.0)
                    else:
                        # とりあえず巨大なスコアのパスがあるとしておく. パスなしでもいい.
                        score = LARGE_SCORE
                    beam_graph.path_map.set_path(pre_node_id, node_id, score)
            # このポイントにおける各ノードのスコアを出し、上位のノード以外は消す
            beam_graph.top_nodes_in_point(i)
    
        else:
            node_id = (u"</s>", i)
            beam_graph.node_map.set_node(node_id, i)
            beam_graph.set_end_node_id(node_id)
            
            pos = u"</s>"

            # 最終ノードと、前のポイントのノードリストの間にパスを張る
            pre_nodes = beam_graph.node_map.get_node_ids_by_point(i-1)
            pwp = 1.0
            for pre_node_id in pre_nodes:
                pre_pos = pre_node_id[0]
                prob = hmm.pos_pos_prob(pre_pos, pos) * pwp
    
                if prob > 0:
                    score = -1.0 * math.log(prob, 2.0)
                else:
                    # とりあえず巨大なスコアのパスがあるとしておく. パスなしでもいい.
                    score = LARGE_SCORE
                beam_graph.path_map.set_path(pre_node_id, node_id, score)

            # 最終ノードのスコアを出す
            beam_graph.top_nodes_in_point(i)

    best_path =  beam_graph.get_best_path()
    return [p for p, idx in best_path]

hmm = HMM(lambda_unigram=0.95, all_word_num=long(10**6))
hmm.read_model(sys.argv[1])

beam_width = int(sys.argv[2])


normal_pos_list = list({
    pre_pos for pre_pos in hmm.pos_pos_model.keys() 
    if pre_pos not in [u"<s>", u"</s>"]
})

for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")
    words.insert(0, u"<s>")
    words.append(u"</s>")
    best_poses = get_best_poses(words, normal_pos_list, hmm, beam_width)
    print u" ".join(best_poses[1:-1]).encode("utf-8")
