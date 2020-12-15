import numpy as np
#import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior() 

y_data = np.matrix([5091.25,5524.50,-946.50,6197.75,863.25,25.25,7097.50,696.00,8942.00,4743.25,1884.00,-1359.17,1081.25,567.00,5944.50,607.25,20508.00,502.50,2996.75,7970.25,-217.25,16192.50,10940.50,7227.25,6010.25,2319.25,-1075.75,-690.00,1372.00,-157.75,4320.00,8569.25,803.75,4909.25,364.50,1219.50,551.25,1253.75,9498.75,4664.25,7338.00,534.75,5330.75,591.75,-638.00,1547.25,226.00,15155.50,4170.00,-1019.50,2567.50,-244.00,-1722.00,11576.50,-1584.50,-42.75,-250.75,-217.75,-636.75,31.75,-842.25,648.75,1412.25,3210.75,-264.50,705.25,2003.00,125.50,1782.00,5190.25,7760.25,9907.00,109.75,2090.25,3282.00,-917.75,-28.75,5183.00,-245.00,1308.25,52.25,425.25,658.75,-260.00,796.25,-733.25,10279.25,6639.00,245.00,41.50,811.50,691.50,753.25,-605.25,-1432.75,-338.50,2834.75,5184.75])
x_data = np.matrix([0.0725865011,0.0598646487,0.0519949637,0.056402813,0.0480704066,0.0680963773,0.0512880562,0.0620392697,0.0601740973,0.0346519671,0.063253012,0.0544706879,0.0642003438,0.0683654292,0.0471772467,0.1075246355,0.0352214715,0.0579361585,0.0640376972,0.054895193,0.075943188,0.0840013602,0.0861632793,0.0596001584,0.0656253798,0.0454511608,0.0478538492,0.0569965437,0.0530803963,0.0490780739,0.0678636851,0.0461240787,0.0708318695,0.0330527541,0.0559880031,0.0451222629,0.0464938941,0.0721659616,0.07109263,0.0653361006,0.0491303297,0.0730515249,0.0450243763,0.0541871667,0.0538637508,0.0473036185,0.0727988974,0.0582096627,0.0544977814,0.0720638987,0.039810294,0.0456806154,0.0780608786,0.0564470721,0.04997961,0.0513295554,0.0338997724,0.0512921014,0.0545121663,0.0500579338,0.0479348284,0.0582510486,0.0520301097,0.0588909118,0.0413031736,0.0593563688,0.0391415037,0.0608143005,0.0629239396,0.069936245,0.0839208774,0.063818132,0.046554074,0.0565086412,0.0359517145,0.0478933738,0.0692487257,0.0693207686,0.067808669,0.0471695862,0.0501321639,0.0623854594,0.0301317441,0.0308992001,0.043094636,0.0628783452,0.0976832223,0.0427173957,0.0457189581,0.0483995604,0.0429025568,0.0431436519,0.0535376216,0.064807082,0.0389205755,0.0496983655,0.0583624042])
plt.plot(x_data.T, y_data.T, 'x') # The 'x' means that data points will be marked with an x
plt.xlabel('Ændring i Netto IndbyggertalKommuner')
plt.ylabel('Ændring i Kvm priser')
plt.title('Ændring fra 2010 til 2020')
plt.show()

x = tf.placeholder(tf.float32, shape=(1, None))

a = tf.get_variable("a", shape=())
b = tf.get_variable("b", shape=())

y_predicted = a*x + b #y_predicted is not a TensorFlow variable -> not directly trainable, we have defined a model and we could call y_predicted a TensorFlow node.

y = tf.placeholder(tf.float32, shape=(1, None)) # we need to define the loss function, the loss function evaluates the created model - the smaller the loss values the better
                                                # Since y is made from our outside data - and we did not train it, we hold it as a tf.placeholder
                                                # the loss is made from the normal quadratic distance measure L(a,b)=∑i=1 (y′(xi,a,b)−yi)^2, We want a low distance from the model to the actual data.
L = tf.reduce_sum((y_predicted - y)**2)     # tf.reduce_sum  adds up all the numbers stored in a vector. It "reduces" the vector to a sum. "reduce" here has nothing to           
                                            #do with the minimization of the loss function.


optimizer = tf.train.AdamOptimizer(learning_rate=0.2).minimize(L)   # we now a gradient descent algorithm to minimize the loss function, thus attempt to find a optimal a and b.

                                                                    #, tf.train.AdamOptimizer perfomrs gradient descent, thus the algorithm increase or decrease in the magnitude of a property, we here only gets an optimizer object which we can us to minimize L
                                                                    #In each iteration, gradient descent produces a small step that is determined by the derivative(the difference) of the loss function. Learning rate is relative size to the step. If we take larger steps, we can use a larger learning rate. A larger learning rate makes us converge faster, since we cover a larger distance in each iteration. So it can converge to fast, so reliability of minimum loss will suffer. 
session = tf.Session()                                              # so far we have been setting up the input for TensorFlow, so now we want to "create a session" for computing.
                                                                    # Session is the way to perform actual computations with TensorFlow

session.run(tf.global_variables_initializer())                      # We neeed to initialize a and b to actual numeric value, so we can converge towards converged a and b og the linear equation.
                                                                    # gradient descent needs initialized values to work with. The parameter is what computation to start.

                                                                    #And we need enough iterations to converge to an acutual minimum, which we will monitor to be sure we have converged. 

# We use session.run for a session of computation - and we pass it an array for the actual computations we want to performe.

# we want to perform 4 computations. The optimizer performs 0.2 step of gradient descent, and updates a and b. L holds the current value of the loss function and a,b holds the current value of a and b.
# this is printet - so that we can see that the data converges. Only the optimizer does not return a value, so so we only need 3 variables to hold the current values. 


for t in range(100):
    _, current_loss, current_a, current_b = session.run([optimizer, L, a, b], feed_dict={
        x: x_data,
        y: y_data
    })
    print("t = %g, loss = %g, a = %g, b = %g" % (t, current_loss, current_a, current_b))