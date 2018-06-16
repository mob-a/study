import tensorflow as tf


def sample9():
    # ついに最適化アルゴリズムに到達. 勾配降下法で重回帰をやる.
    # data
    X = [[1.0, 2.0, 5.0], [1.0, 3.0, 3.0], [1.0, 4.0, -1.0], [1.0, -2.0, 3.0]]
    Y = [[-10.0], [-2.0], [12.0], [-13.0]]
    data_dim = 3
    #
    op_iter_num = 40
    assign_iter_num = 5
    with tf.Session() as sess:
        #
        xs = tf.placeholder(tf.float32, shape=[None, data_dim])  # (4,3)
        ys = tf.placeholder(tf.float32, shape=[None, 1])

        w = tf.Variable(tf.ones([data_dim, 1]), dtype=tf.float32)
        lr = 0.01

        # opループ
        ops = [None] * op_iter_num
        for i in range(op_iter_num):
            # matmulで次元合わせるのが大変.
            # 行列同士の場合 (N,M)*(M,L) => (N,L)
            if i > 0:
                diffs = tf.matmul(xs, ops[i-1]) - ys
                grad = 2.0 * tf.matmul(tf.transpose(xs), diffs)
                ops[i] = ops[i-1] - lr * grad
            else:
                diffs = tf.matmul(xs, w) - ys                      # (4,3)*(3,1)=>(4,1)
                grad = 2.0 * tf.matmul(tf.transpose(xs), diffs)    # (3,4)*(4,1)=>(3,1)
                ops[i] = w - lr * grad

        # eval
        eval_op = tf.reduce_sum(
            tf.square(tf.matmul(xs, w) - ys)
        )

        # assignループ
        assign_op = tf.assign(w, ops[-1])
        sess.run(tf.global_variables_initializer())
        for j in range(assign_iter_num):
            print("assign loop:", (j+1))
            print(
                "weight:",
                sess.run(assign_op, feed_dict={
                    xs: X,
                    ys: Y,
                })
            )
            print(
                "train error:",
                sess.run(eval_op, feed_dict={
                    xs: X,
                    ys: Y,
                })
            )
            print("----------------")


if __name__ == "__main__":
    sample9()
