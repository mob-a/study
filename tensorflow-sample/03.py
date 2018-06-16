import tensorflow as tf


def sample3():
    with tf.Session() as sess:
        # 1次元テンソルとスカラー値は別物
        x = tf.Variable(tf.zeros([1], dtype=tf.int32), dtype=tf.int32)
        print(x)

        y = tf.Variable(tf.zeros([], dtype=tf.int32), dtype=tf.int32)
        print(y)

        smul = tf.scalar_mul(y, x)
        print(smul)

        sess.run(tf.global_variables_initializer())
        print(sess.run(smul))

        try:
            tf.scalar_mul(x, y)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    print("# 3 #########################")
    sample3()
