# -*- coding: utf-8 -*-
from collections import Counter
import sys
from STOPWORDS import STOPWORDS

def read_cluster(filename):
    docid2clusterid = {}
    with open(filename, "r") as f:
        for fline in f.readlines():
            fline = unicode(fline, "utf-8")
            fline = fline.rstrip(u"\r\n")
            cluster_id, docids_str = fline.split(u"\t")
        
            for docid in docids_str.split(u"_"):
                docid2clusterid[int(docid)] = int(cluster_id)
    return docid2clusterid

cluster_words = {}
cluster_unique_words = {}
global_words = Counter()

docid2clusterid = read_cluster(sys.argv[1])
for clusterid in set(docid2clusterid.values()):
    cluster_words[clusterid] = Counter()
    cluster_unique_words[clusterid] = Counter()
for docid, line in enumerate(sys.stdin):
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")
    cluster_id = docid2clusterid[docid]

    for word in words:
        if word in STOPWORDS:
            continue
        cluster_words[cluster_id][word] += 1
        global_words[word]+=1

    for uword in set(words):
        if uword in STOPWORDS:
            continue
        cluster_unique_words[cluster_id][uword] += 1

for cluster_id in set(docid2clusterid.values()):
    print "##############################"
    print cluster_id
    print "##############################"
    # for word, ucount in cluster_unique_words[cluster_id].most_common(50):
    for word, cnt in cluster_words[cluster_id].most_common(50):
        ucount = cluster_unique_words[cluster_id][word]
        count = cluster_words[cluster_id][word]
        print "%s\t%s\t%s"%(word.encode("utf-8"), str(ucount), str(count))
