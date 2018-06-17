import tensorflow as tf


def sample10():
    # einsum実験
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
        b = tf.constant([  # (3,2)
            [10, 100],
            [20, 200],
            [30, 300],
        ])
        print(a)
        print(b)
        print("-------------------")

        # 1つのテンソルをreduce (reduce_sumでいいのでは)
        op1 = tf.einsum("ijk->ik", a)  # (3,2,4)->(3,4)
        print(op1)
        print(sess.run(op1))
        print("-------------------")  # 6,8,10,12

        # 共通次元で和をとる
        op2 = tf.einsum("ijk,ij->k", a, b)  # (3,2,4)~(3,2)->(4)
        print(op2)
        print(sess.run(op2))
        print("-------------------")  # 1*10 + 9*20 + 17*30 + 5*100 + 13*200 + 21*300 = 10100

        # 共通次元で積をとる
        op3 = tf.einsum("ijk,ij->ijk", a, b)  # (3,2,4)~(3,2)->(3,2,4)
        print(op3)
        print(sess.run(op3))
        print("-------------------")  # [10 20 30 40][500 600 700 800]

        # 共通次元で積をとったあと和をとる
        op4 = tf.einsum("ijk,ij->ik", a, b)  # (3,2,4)~(3,2)->(3,4)
        print(op4)
        print(sess.run(op4))
        print("-------------------")  # [10+500 20+600 30+700 40+800] => [510, 620, 730, 840]


if __name__ == "__main__":
    sample10()
