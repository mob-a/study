import tensorflow as tf


def sample2():
    with tf.Session() as sess:
        # https://web.stanford.edu/class/cs20si/2017/lectures/slides_02.pdf
        # 27-31ページあたり. なんとtensorflowはPythonネイティブ型を解釈する.
        print("==========")

        consts = tf.constant([11, 22, 33])
        x = 44
        print(x)
        for i in range(3):
            x += consts[i]
            print(x)
        print("----------")

        sess.run(tf.global_variables_initializer())
        result = sess.run(x)

        print(result)
        print("==========")

    with tf.Session() as sess_:
        print("==========")
        consts_ = tf.constant([11, 22, 33])
        x_ = tf.constant(44)
        print(x_)
        op0_ = tf.add(x_, consts_[0])
        print(op0_)
        op1_ = tf.add(op0_, consts_[1])
        print(op1_)
        op2_ = tf.add(op1_, consts_[2])
        print(op2_)
        print("----------")

        sess_.run(tf.global_variables_initializer())
        result_ = sess_.run(op2_)

        print(result_)
        print("==========")


if __name__ == "__main__":
    sample2()
