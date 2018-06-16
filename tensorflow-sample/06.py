import tensorflow as tf


def sample6():
    # 次元数Noneのplaceholder
    with tf.Session() as sess:
        ph = tf.placeholder(tf.float32, shape=[None, 2])
        op = tf.scalar_mul(tf.constant(2.0), ph)

        print(
            sess.run(op, feed_dict={
                ph: [[10, 20]],
            })
        )

        print(
            sess.run(op, feed_dict={
                ph: [[10, 20],
                     [100, 200],
                     [1000, 2000]],
            })
        )


if __name__ == "__main__":
    sample6()
