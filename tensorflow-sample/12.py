import tensorflow as tf


def sample12():
    # コロン記法
    with tf.Session() as sess:
        #
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
        print(a)
        print("-------------------")
        print(a[1, :, :])  # (3,2,4)->(2,4)
        print(sess.run(a[1, :, :]))
        print("-------------------")
        print(a[:, 1, :])  # (3,2,4)->(3,4)
        print(sess.run(a[:, 1, :]))
        print("-------------------")
        print(a[:, :, 1])  # (3,2,4)->(3,2)
        print(sess.run(a[:, :, 1]))
        print("-------------------")
        print(a[1, 1, :])  # (3,2,4)->(4)
        print(sess.run(a[1, 1, :]))


if __name__ == "__main__":
    sample12()
