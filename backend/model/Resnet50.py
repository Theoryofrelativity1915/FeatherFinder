import tensorflow as tf
from tensorflow import keras
from keras.applications import ResNet50V2
from keras.layers import Flatten, Dense, Dropout, Rescaling, RandomRotation, RandomContrast, RandomCrop, RandomBrightness
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import os
# labels is a list of all 510 unique species with no repeats
TRAIN_DATADIR = "C:\\Datasets\\train"
TEST_DATADIR = "C:\\Datasets\\test"
VAL_DATADIR = "C:\\Datasets\\valid"
IMG_SIZE = 224

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)
train_data = tf.keras.preprocessing.image_dataset_from_directory(
    TRAIN_DATADIR, image_size=(IMG_SIZE, IMG_SIZE), batch_size=256)
class_names = train_data.class_names
train_data = train_data.cache().prefetch(tf.data.AUTOTUNE)

valid_data = tf.keras.preprocessing.image_dataset_from_directory(
    VAL_DATADIR, image_size=(IMG_SIZE, IMG_SIZE), batch_size=256)
valid_data = valid_data.cache().prefetch(tf.data.AUTOTUNE)

testing_data = tf.keras.preprocessing.image_dataset_from_directory(
    TEST_DATADIR, image_size=(IMG_SIZE, IMG_SIZE), batch_size=256)
testing_data = testing_data.cache().prefetch(tf.data.AUTOTUNE)



check_point = keras.callbacks.ModelCheckpoint(filepath="ResNet50.h5",
                                              monitor="val_acc",
                                              mode="max",
                                              save_best_only=True)

early_stopping = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    min_delta=0,
    patience=0,
    verbose=0,
    mode="auto",
    baseline=None,
    restore_best_weights=False,
)


resnet = ResNet50V2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
# Freeze the weights of the pre-trained model
for layer in resnet.layers:
    layer.trainable = False
    
model = keras.models.Sequential()
model.add(Rescaling(1./255))
model.add(RandomRotation(0.5))
# model.add(RandomContrast(0.4))
model.add(RandomCrop(224, 224))
# model.add(RandomBrightness(0.4))
model.add(resnet)
model.add(Flatten())

model.add(Dense(1020, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(510, activation='softmax'))
if __name__ == "main":
    
    # Compile the model
    model.compile(optimizer=Adam(learning_rate=0.0001),
                loss=tf.losses.SparseCategoricalCrossentropy(),
                metrics=['accuracy'])

    history = model.fit(train_data,
                        batch_size=256,
                        epochs=50,
                        validation_data=valid_data,
                        callbacks=[check_point])

    model.evaluate(testing_data)
    # Print the model summary
    model.summary()
    model.evaluate(testing_data)

    model.save(os.path.join('models', 'ResNet50V2.h5'))
    test_loss, test_accuracy = model.evaluate(testing_data, verbose=0)
    print("Loss on test set: {}".format(test_loss))
    print("Accuracy on test set: {:.4f}%".format(test_accuracy*100))

# # Plot training & validation accuracy values
# plt.figure(figsize=(12, 4))

# plt.plot(history.history['acc'])
# plt.plot(history.history['val_acc'])
# plt.title('Model accuracy')
# plt.ylabel('Accuracy')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Validation'], loc='upper left')

# # Plot training & validation loss values
# plt.plot(history.history['loss'])
# plt.plot(history.history['val_loss'])
# plt.title('Model loss')
# plt.ylabel('Loss')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Validation'], loc='upper left')

# plt.show()