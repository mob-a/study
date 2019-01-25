# -*- coding: utf-8 -*-

import sys

counter = {}
for line in sys.stdin:
    line = unicode(line, "utf-8")
    line = line.rstrip(u"\r\n")

    words = line.split(u" ")

    for word in words:
        if word not in counter:
            counter[word] = 0
        counter[word] += 1

for key in sorted(counter.keys()):
    print "%s\t%s" % (key.encode("utf-8"), str(counter[key]))

