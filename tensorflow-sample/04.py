import tensorflow as tf


def sample4():
    with tf.Session() as sess:
        x = tf.Variable(tf.zeros([1], dtype=tf.int32), dtype=tf.int32)
        assign_op = tf.assign(x, tf.constant([11], dtype=tf.int32))
        y = tf.Variable(tf.zeros([1], dtype=tf.int32), dtype=tf.int32)
        add_op = tf.add(x, y)

        sess.run(tf.global_variables_initializer())
        print(sess.run(assign_op))
        print(sess.run(add_op))

    print("---------------")

    with tf.Session() as sess2:
        # assignをrunしない場合、xの値は0のまま
        x2 = tf.Variable(tf.zeros([1], dtype=tf.int32), dtype=tf.int32)
        assign_op2 = tf.assign(x2, tf.constant([11], dtype=tf.int32))  # 使われない
        y2 = tf.Variable(tf.zeros([1], dtype=tf.int32), dtype=tf.int32)
        add_op2 = tf.add(x2, y2)

        sess2.run(tf.global_variables_initializer())
        print(sess2.run(add_op2))

    print("---------------")

    with tf.Session() as sess3:
        # assignの結果をaddに使うなどでもよい
        x3 = tf.Variable(tf.zeros([1], dtype=tf.int32), dtype=tf.int32)
        assign_op3 = tf.assign(x3, tf.constant([11], dtype=tf.int32))
        y3 = tf.Variable(tf.zeros([1], dtype=tf.int32), dtype=tf.int32)
        add_op3 = tf.add(assign_op3, y3)

        sess3.run(tf.global_variables_initializer())
        print(sess3.run(add_op3))
        print(sess3.run(x3))

    print("---------------")

    with tf.Session() as sess4:
        # randomを2回assignすると別の結果
        x4 = tf.Variable(tf.zeros([1], dtype=tf.float32), dtype=tf.float32)
        assign_op4 = tf.assign(x4, tf.random_uniform([1]))

        y4 = tf.Variable(tf.constant([100.0]), dtype=tf.float32)
        add_op_y4 = tf.add(assign_op4, y4)

        z4 = tf.Variable(tf.constant([200.0]), dtype=tf.float32)
        add_op_z4 = tf.add(assign_op4, z4)

        sess4.run(tf.global_variables_initializer())
        print(sess4.run(add_op_y4))
        print(sess4.run(add_op_z4))

    print("---------------")

    with tf.Session() as sess5:
        # 無意味に変数宣言とassignを分けるのはやめる.
        # https://stackoverflow.com/questions/34888235/how-do-i-generate-a-random-vector-in-tensorflow-and-maintain-it-for-further-use
        x5 = tf.Variable(tf.random_uniform([1]), dtype=tf.float32)
        y5 = tf.Variable(tf.constant([100.0]), dtype=tf.float32)
        z5 = tf.Variable(tf.constant([200.0]), dtype=tf.float32)

        add_op_y5 = tf.add(x5, y5)
        add_op_z5 = tf.add(x5, z5)

        sess5.run(tf.global_variables_initializer())
        print(sess5.run(add_op_y5))
        print(sess5.run(add_op_z5))

    print("---------------")

    with tf.Session() as sess6:
        # 一応、assignだけ別実行してもよい
        x6 = tf.Variable(tf.random_uniform([1]), dtype=tf.float32)
        y6 = tf.Variable(tf.constant([100.0]), dtype=tf.float32)
        z6 = tf.Variable(tf.constant([200.0]), dtype=tf.float32)

        assign_op6 = tf.assign(x6, tf.random_uniform([1]))
        add_op_y6 = tf.add(x6, y6)
        add_op_z6 = tf.add(x6, z6)

        sess6.run(tf.global_variables_initializer())
        sess6.run(assign_op6)
        print(sess6.run(add_op_y6))
        print(sess6.run(add_op_z6))


if __name__ == "__main__":
    print("# 4 #########################")
    sample4()
