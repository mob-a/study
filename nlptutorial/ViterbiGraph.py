# -*- coding: utf-8 -*-
class Node(object):
    def __init__(self, node_id, point, min_score=None, prev_node_id=None):
        self.node_id = node_id
        self.point = point
        self.min_score = min_score
        self.prev_node_id = prev_node_id

class NodeMap(object):
    def __init__(self):
        self.node_dict = {}
        self.point2nodes = {}

    def set_node(self, node_id, point, min_score=None, prev_node_id=None):
        self.node_dict[node_id] = Node(node_id=node_id,
                                       point=point,
                                       min_score=min_score,
                                       prev_node_id=prev_node_id)

        if point not in self.point2nodes:
            self.point2nodes[point] = []
        self.point2nodes[point].append(self.node_dict[node_id])

    def update_node(self, node_id, min_score, prev_node_id):
        self.node_dict[node_id].min_score = min_score
        self.node_dict[node_id].prev_node_id = prev_node_id

    def get_min_score(self, node_id):
        return self.node_dict[node_id].min_score

    def get_prev_node_id(self, node_id):
        return self.node_dict[node_id].prev_node_id

    def get_point(self, node_id):
        return self.node_dict[node_id].point

    def get_node_ids_sorted_by_point(self):
        return sorted(self.node_dict.keys(), key=lambda k: self.node_dict[k].point)

    def get_node_ids_by_point(self, point):
        return [node.node_id for node in self.point2nodes[point]]

class PathMap(object):
    # path_dict は、paths["n3"] = [("n1", 1.0), ("n2", 2.0)]のように
    # キーを 矢印の先のnode_id に、値は(矢印の元のnode_id, パススコア)にした辞書
    def __init__(self):
        self.path_dict = {}

    def set_path(self, src_node_id, dest_node_id, score):
        if not dest_node_id in self.path_dict:
            self.path_dict[dest_node_id] = []
        self.path_dict[dest_node_id].append((src_node_id, score))        


class ViterbiGraph(object):
    # 制約条件
    # - パスは、(pointが小さいノード -> pointが大きいノード) の向きのみ
    #   ノード間に前後関係がある
    # - 連結グラフにする. 孤立したノードは作らない.
    # - pointが最小値をとるノードは1つのみ (開始ノード)
    # - pointが最大値をとるノードは1つのみ (終了ノード)
    # - 開始ノードのスコア初期値はNoneにしない. 適当な実数値を持たせておく.
    def __init__(self, node_map, path_map):
        self.node_map = node_map
        self.path_map = path_map

    def set_start_node_id(self, start_node_id):
        self.start_node_id =  start_node_id

    def set_end_node_id(self, end_node_id):
        self.end_node_id =  end_node_id

    def scores_in_point(self, point):
        for node_id in self.node_map.get_node_ids_by_point(point):
            min_score = None
            best_src_node_id = None
            for src_node_id, path_score in self.path_map.path_dict[node_id]:
                src_score = self.node_map.get_min_score(src_node_id)
                new_score = src_score + path_score

                if (min_score is None) or (min_score > new_score):
                    min_score = new_score
                    best_src_node_id = src_node_id
            self.node_map.update_node(node_id, min_score, best_src_node_id)

    def get_best_path(self):
        node_ids = []

        node_id = self.end_node_id
        while True:
            node_ids.append(node_id)
            if node_id == self.start_node_id:
                break
            node_id = self.node_map.get_prev_node_id(node_id)
            
        node_ids.reverse()
        return node_ids

    def solve(self):
        start_point = self.node_map.get_point(self.start_node_id)
        for point in sorted(self.node_map.point2nodes.keys()):
            if point <= start_point:
                continue
            self.scores_in_point(point)

class BeamGraph(ViterbiGraph):
    def __init__(self, node_map, path_map, beam_width):
        self.node_map = node_map
        self.path_map = path_map
        self.beam_width = beam_width

    def top_nodes_in_point(self, point):
        nodeid2score = {}
        for node_id in self.node_map.get_node_ids_by_point(point):
            min_score = None
            best_src_node_id = None
            for src_node_id, path_score in self.path_map.path_dict[node_id]:
                src_score = self.node_map.get_min_score(src_node_id)
                new_score = src_score + path_score

                if (min_score is None) or (min_score > new_score):
                    min_score = new_score
                    best_src_node_id = src_node_id
            self.node_map.update_node(node_id, min_score, best_src_node_id)
            nodeid2score[node_id] = min_score

        # スコアが小さいもの beam_width 件以降のノードは削除する
        sorted_node_ids = sorted(nodeid2score.keys(), key=lambda k:nodeid2score[k])
        for i, node_id in enumerate(sorted_node_ids):
            if i >= self.beam_width:
                self.delete_node(node_id, point)


    def delete_node(self, node_id, point):
        del self.node_map.node_dict[node_id]
        
        del self.path_map.path_dict[node_id]
        
        del_idx = None
        for i, node in enumerate(self.node_map.point2nodes[point]):
            if node.node_id == node_id:
                del_idx = i
                break
        del self.node_map.point2nodes[point][del_idx]

