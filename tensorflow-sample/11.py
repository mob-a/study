import tensorflow as tf


def sample11():
    with tf.Session() as sess:
        # 異なる軸数でのadd,multiply
        a = tf.constant([  # (3,2,4)
            [
                [1, 2, 3, 4], [5, 6, 7, 8]
            ],
            [
                [9, 10, 11, 12], [13, 14, 15, 16]
            ],
            [
                [17, 18, 19, 20], [21, 22, 23, 34]
            ]
        ])
        b = tf.constant([  # (2,4)
            [10, 100, 1000, 10000], [20, 200, 2000, 20000],
        ])
        print(a)
        print(b)

        print("-------------------")
        addop = tf.add(a, b)  # (3,2,4)+(2,4)->(3,2,4)
        print(addop)
        print(sess.run(addop))
        # [11,102,1003,10004][25,206,2007,20008]
        # [19,110,1011,10012][33,214,2015,20016]

        print("-------------------")
        mulop = tf.multiply(a, b)  # (3,2,4)*(2,4)->(3,2,4)
        print(mulop)
        print(sess.run(mulop))
        # [10,200,300,4000],[100,1200,14000,160000]
        # [90,1000,11000,120000],[260,2800,30000,320000]


if __name__ == "__main__":
    sample11()
