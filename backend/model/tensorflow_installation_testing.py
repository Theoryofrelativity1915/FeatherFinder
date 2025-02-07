import tensorflow as tf
import time
from tensorflow.keras.backend import clear_session
# List available physical devices
physical_devices = tf.config.list_physical_devices('GPU')
print("Num GPUs Available: ", len(physical_devices))

if physical_devices:
    print("TensorFlow is using the GPU")
    for gpu in physical_devices:
        tf.config.experimental.set_memory_growth(gpu, True)
        print(gpu)
else:
    print("TensorFlow is not using the GPU")
# Simple TensorFlow computation to test GPU utilization
a = tf.random.normal((5000, 5000))
b = tf.random.normal((5000, 5000))

# Perform a matrix multiplication
start_time = time.time()
result = tf.matmul(a, b)
end_time = time.time()
clear_session()
print("Operation completed")
print(f"Time taken for computation: {end_time - start_time} seconds")
