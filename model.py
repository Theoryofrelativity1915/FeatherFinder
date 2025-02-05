import tensorflow as tf
from tensorflow import keras
from keras import regularizers
from keras.models import Sequential
from keras.layers import Conv2D, Flatten, MaxPooling2D, Dense, Dropout, BatchNormalization, ReLU, RandomRotation, RandomContrast, Rescaling
import os
import matplotlib.pyplot as plt
import numpy as np

#labels is a list of all 510 unique species with no repeats
TRAIN_DATADIR = "C:\\Datasets\\train"
TEST_DATADIR = "C:\\Datasets\\test"
VAL_DATADIR = "C:\\Datasets\\valid"
IMG_SIZE = 224

data_augmentation = Sequential()
data_augmentation.add(RandomContrast(0.4))
data_augmentation.add(RandomRotation(0.4))


#creates a data pipeline rather than loading all 89,000 images into VRAM
train_data = tf.keras.preprocessing.image_dataset_from_directory(TRAIN_DATADIR, image_size=(IMG_SIZE, IMG_SIZE), batch_size=32)
class_names = train_data.class_names
if __name__ == "__main__":
    augmented_train_data = train_data.map(lambda x, y: (data_augmentation(x, training = True), y))
    augmented_train_data = augmented_train_data.cache().prefetch(tf.data.AUTOTUNE)

testing_data = tf.keras.preprocessing.image_dataset_from_directory(TEST_DATADIR, image_size=(IMG_SIZE, IMG_SIZE), batch_size=32)
testing_data = testing_data.cache().prefetch(tf.data.AUTOTUNE)

valid_data = tf.keras.preprocessing.image_dataset_from_directory(VAL_DATADIR, image_size=(IMG_SIZE, IMG_SIZE), batch_size=32)
valid_data = valid_data.cache().prefetch(tf.data.AUTOTUNE)



model = Sequential()
model.add(Rescaling(1./255))
model.add(Conv2D(32, (2,2), 1, input_shape=(IMG_SIZE, IMG_SIZE, 3)))
model.add(BatchNormalization())
model.add(MaxPooling2D())
model.add(ReLU())

model.add(Conv2D(64, (2,2), 1))
model.add(BatchNormalization())
model.add(MaxPooling2D())
model.add(ReLU())


model.add(Conv2D(128, (2,2), 1))
model.add(BatchNormalization())
model.add(MaxPooling2D())


model.add(Conv2D(256, (2,2), 1))
model.add(BatchNormalization())
model.add(MaxPooling2D())
model.add(ReLU())

model.add(Conv2D(512, (2,2), 1))
model.add(BatchNormalization())
model.add(MaxPooling2D())
model.add(ReLU())

model.add(Conv2D(64, (2,2), 1))
model.add(BatchNormalization())
model.add(MaxPooling2D())
model.add(ReLU())



model.add(Flatten())

model.add(Dense(1020, activation='relu', kernel_regularizer=regularizers.l2(0.001)))
model.add(Dropout(0.5))
model.add(Dense(510, activation='softmax'))

if __name__ == "__main__":
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss=tf.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
    model.fit(train_data, epochs=10, validation_data=valid_data)
    model.summary()
    model.evaluate(testing_data)

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4), loss=tf.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
    model.fit(train_data, epochs=10, validation_data=valid_data)
    model.evaluate(testing_data)

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5), loss=tf.losses.SparseCategoricalCrossentropy(), metrics=['accuracy'])
    model.fit(train_data, epochs=10, validation_data=valid_data)
    model.evaluate(testing_data)


    model.save(os.path.join('models', 'BirdClassificationV6.h5'))

    test_loss, test_accuracy = model.evaluate(testing_data, verbose=0)
    print("Loss on test set: {}".format(test_loss))
    print("Accuracy on test set: {:.4f}%".format(test_accuracy*100))
