import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt␍
from BirdClassificationV6 import class_names, testing_data␍
␍
# Initialize constants␍
IMAGE_DIRECTORY = 'C:\\Datasets\\images to predict\\'␍
IMG_SIZE = 224␍
PREDICT_IMG_LABELS = ["African Crowned Crane", "African Crowned Crane", "African Crowned Crane", "African Crowned Crane", "African Crowned Crane", "Bald Eagle"]␍
IMAGES_TO_PREDICT = [plt.imread(os.path.join(IMAGE_DIRECTORY, image)) for image in os.listdir(IMAGE_DIRECTORY)]␍
# IMAGES_TO_PREDICT = [plt.imread(image) for image in IMAGES_TO_PREDICT]␍
# Load pre-trained model␍
model = tf.keras.models.load_model(os.path.join('models', 'BirdClassificationV6.h5'))␍
␍
# #Evaluate and print models performance␍
test_loss, test_accuracy = model.evaluate(testing_data)␍
print("Loss on test set: {}".format(test_loss))␍
print("Accuracy on test set: {:.4f}%".format(test_accuracy*100))␍
␍
␍
predicted_labels = []␍
for i in range(1, 7):
    ␍
    image_directory_path = os.path.join(IMAGE_DIRECTORY, (str(i)+".jpg"))␍
    image = tf.keras.utils.load_img(image_directory_path)␍
    input_arry = tf.keras.utils.img_to_array(image)␍
    input_arry = np.array([input_arry])␍
    input_arry = tf.image.resize(input_arry, (224, 224))␍
    predictions = model.predict(input_arry, verbose=0)␍
    score = tf.nn.softmax(predictions[0])␍
    predicted_class = class_names[np.argmax(predictions)]␍
␍
predicted_labels.append(predicted_class)␍
print('Bird is most likely a ', predicted_class)␍
␍
␍
␍
plt.figure(figsize=(8, 8))␍
ax1 = plt.subplot(231)␍
ax1.tick_params(left=False, bottom=False)␍
ax1.set_yticklabels('')␍
ax1.set_xticklabels('')␍
ax1.set_title(PREDICT_IMG_LABELS[0])␍
ax1.set_xlabel("Predicted: " + predicted_labels[0], **{'size': '8'})␍
ax1.imshow(IMAGES_TO_PREDICT[0])␍
␍
ax2 = plt.subplot(232)␍
ax2.tick_params(left=False, bottom=False)␍
ax2.set_yticklabels('')␍
ax2.set_xticklabels('')␍
ax2.set_title(PREDICT_IMG_LABELS[1])␍
ax2.set_xlabel("Predicted: " + predicted_labels[1], **{'size': '8'})␍
ax2.imshow(IMAGES_TO_PREDICT[1])␍
␍
␍
ax3 = plt.subplot(233)␍
ax3.tick_params(left=False, bottom=False)␍
ax3.set_yticklabels('')␍
ax3.set_xticklabels('')␍
ax3.set_title(PREDICT_IMG_LABELS[2])␍
ax3.set_xlabel("Predicted: " + predicted_labels[2], **{'size': '8'})␍
ax3.imshow(IMAGES_TO_PREDICT[2])␍
␍
ax4 = plt.subplot(234)␍
ax4.tick_params(left=False, bottom=False)␍
ax4.set_yticklabels('')␍
ax4.set_xticklabels('')␍
ax4.set_title(PREDICT_IMG_LABELS[3])␍
ax4.set_xlabel("Predicted: " + predicted_labels[3], **{'size': '8'})␍
ax4.imshow(IMAGES_TO_PREDICT[3])␍
␍
ax5 = plt.subplot(235)␍
ax5.tick_params(left=False, bottom=False)␍
ax5.set_yticklabels('')␍
ax5.set_xticklabels('')␍
ax5.set_title(PREDICT_IMG_LABELS[4])␍
ax5.set_xlabel("Predicted: " + predicted_labels[4], **{'size': '8'})␍
ax5.imshow(IMAGES_TO_PREDICT[4])␍
␍
ax6 = plt.subplot(236)␍
ax6.tick_params(left=False, bottom=False)␍
ax6.set_yticklabels('')␍
ax6.set_xticklabels('')␍
ax6.set_title(PREDICT_IMG_LABELS[5])␍
ax6.set_xlabel("Predicted: " + predicted_labels[5], **{'size': '8'})␍
ax6.imshow(IMAGES_TO_PREDICT[5])␍
plt.subplots_adjust(hspace=0.2, wspace=0.3)␍
plt.show()
