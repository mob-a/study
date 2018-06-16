import tensorflow as tf


def sample5():
    # placeholderの基本
    with tf.Session() as sess:
        ph_tensor = tf.placeholder(tf.float32, shape=[1, 2])
        ph_scalar = tf.placeholder(tf.float32, shape=[])
        op = tf.scalar_mul(ph_scalar,
                           tf.add(tf.constant([[100.0], [200.0]], dtype=tf.float32), ph_tensor))

        print(
            sess.run(op, feed_dict={
                ph_tensor: [[10, 20]],
                ph_scalar: 3
            })
        )


if __name__ == "__main__":
    sample5()
