import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior() 
import pandas as pd
import matplotlib.pyplot as plt

#Code explained in simple linear regression
D = np.matrix(pd.read_csv("/Users/martin/Documents/fortjenestIndbvækKvmPrisÆndring.csv", header=None).values)

# First n columns into X_data and flip it
X_data = D[:, 0:2].transpose()

# last column into y_data and flip it
y_data = D[:, 2].transpose()

n = 2

x = tf.placeholder(tf.float32, shape=(n, None))
y = tf.placeholder(tf.float32, shape=(1, None))

A = tf.get_variable("A", shape=(1, n))
b = tf.get_variable("b", shape=())

y_predicted = tf.matmul(A, x) + b

L = tf.reduce_sum((y_predicted - y)**2)

optimizer = tf.train.AdamOptimizer(learning_rate=50).minimize(L)

session = tf.Session()
session.run(tf.global_variables_initializer())

for t in range(500000):
    _, current_loss, current_A, current_b = session.run([optimizer, L, A, b], feed_dict={
        x: X_data,
        y: y_data
    })
    if t > 485000:
        print("t = %g, loss = %g, A = %s, b = %g" % (t, current_loss, str(current_A), current_b))
