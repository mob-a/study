import tensorflow as tf


def sample1():
    with tf.Session() as sess:
        #
        #  |--(a)--|
        #  v       |
        # [x] ----(+)
        #      |
        # <1> -|
        #
        # https://www.tensorflow.org/api_docs/python/tf/Session#run
        # The value returned by run() has the same shape as the fetches argument,
        # where the leaves are replaced by the corresponding values returned by TensorFlow.

        # tf.assign
        # https://www.tensorflow.org/api_docs/python/tf/assign
        # This operation outputs a Tensor that holds the new value of 'ref' after the value has been assigned.
        # This makes it easier to chain operations that need to use the reset value.

        # というわけで、runの戻り値はrunの引数にしたassign_opの戻り値で、それはassign後のxの値

        x = tf.Variable(tf.zeros([], dtype=tf.int32), dtype=tf.int32)
        const = tf.constant(1, dtype=tf.int32)
        add_op = tf.add(x, const)
        assign_op = tf.assign(x, add_op)
        sess.run(tf.global_variables_initializer())

        result = sess.run(assign_op)
        print(result)

        result = sess.run(assign_op)
        print(result)

        result = sess.run(assign_op)
        print(result)


if __name__ == "__main__":
    sample1()
