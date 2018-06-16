import tensorflow as tf


def sample7():
    # opループ. よくあるsqrtを題材にやる.
    iter_num = 200
    with tf.Session() as sess:
        src = tf.placeholder(tf.float32, shape=[None])

        # 次元数不定のplaceholderと同じ次元数のVariableやconstantはむずい
        # https://stackoverflow.com/questions/35853483/tensorflow-constant-with-variable-size
        #  initial = tf.Variable(tf.ones(tf.shape(src)), dtype=tf.float32) <= これは動かない
        initial = tf.ones(tf.shape(src), dtype=tf.float32)
        ops = [None] * iter_num
        for i in range(iter_num):
            if i > 0:
                ops[i] = tf.scalar_mul(tf.constant(0.5), tf.add(ops[i-1], tf.div(src, ops[i-1])))
            else:
                # 0.5 * (initial + src / initial) と書いてもいい
                ops[i] = tf.scalar_mul(tf.constant(0.5), tf.add(initial, tf.div(src, initial)))

        sess.run(tf.global_variables_initializer())
        print(
            sess.run(ops[-1], feed_dict={
                src: [5.0]
            })
        )
        print(
            sess.run(ops[-1], feed_dict={
                src: [0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 100.0, 1000.0, 10000.0]
            })
        )


if __name__ == "__main__":
    sample7()
