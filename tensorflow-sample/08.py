import tensorflow as tf


def sample8():
    # assignループ (中はopループ). 今回もsqrtをやる.
    # 次元数は事前に定義する.
    dim = 5
    op_iter_num = 3
    assign_iter_num = 10
    with tf.Session() as sess:
        src = tf.placeholder(tf.float32, shape=[dim])
        current_result = tf.Variable(tf.ones([dim]))

        # opループ
        ops = [None] * op_iter_num
        for i in range(op_iter_num):
            if i > 0:
                ops[i] = tf.scalar_mul(tf.constant(0.5), tf.add(ops[i-1], tf.div(src, ops[i-1])))
            else:
                ops[i] = tf.scalar_mul(tf.constant(0.5), tf.add(current_result, tf.div(src, current_result)))

        # assignループ
        assign_op = tf.assign(current_result, ops[-1])
        sess.run(tf.global_variables_initializer())
        for j in range(assign_iter_num):
            print(
                sess.run(assign_op, feed_dict={
                    src: [0.5, 1.0, 2.0, 10.0, 10000.0],
                })
            )


if __name__ == "__main__":
    sample8()
