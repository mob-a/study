# -*- coding: utf-8 -*-
import sys
import math
from ViterbiGraph import NodeMap, PathMap, ViterbiGraph
from HMM import HMM

hmm = HMM(lambda_unigram=0.95, all_word_num=long(10**6))
hmm.read_model(sys.argv[1])
LARGE_SCORE = 1.0e+10

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
            pos = node_id[0]
            if i == len(words) - 1:
                # 最後の品詞</s>は品詞-単語確率1.0としておく
                pwd = 1.0
            else:
                pwp = hmm.pos_word_prob(pos, word)

            for pre_node_id in pre_nodes:
                pre_pos = pre_node_id[0]

                prob = hmm.pos_pos_prob(pre_pos, pos) * pwp
                if prob > 0:
                    score = -1.0 * math.log(prob, 2.0)
                    pathmap.set_path(pre_node_id, node_id, score)
                else:
                    # とりあえず巨大なスコアのパスがあるとしておく. パスなしでもいい.
                    pathmap.set_path(pre_node_id, node_id, LARGE_SCORE)

    viterbigraph = ViterbiGraph(nodemap, pathmap)
    viterbigraph.set_start_node_id((u"<s>", 0))
    viterbigraph.set_end_node_id((u"</s>", len(words)-1))

    viterbigraph.solve()
    best_path  = viterbigraph.get_best_path()

    print u" ".join(
        [pos for pos, idx in best_path[1:-1]]
    ).encode("utf-8")
