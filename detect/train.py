import csv
import glob

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from model import Classifier, HISTORY_SIZE

label = np.zeros((4, 1000, 2))
label[:,:,0] = 1
label[0,400:520] = [0,1]
label[1,450:650] = [0,1]
label[2,390:530] = [0,1]
label[3,420:550] = [0,1]

X_train = []
Y_train = []

for filename, lab in zip(glob.glob("../data/SMILE_GOOD/*.csv"), label[:3]):
    with open(filename, "rt") as f:
        reader = csv.reader(f)

        data = []
        for row in reader:
            if len(row) > 1:
                data.append(float(row[1]))
        data = np.float32(data)

    data = np.expand_dims(data, -1)
    data = np.pad(data, ((HISTORY_SIZE // 2, HISTORY_SIZE // 2), (0,0)), mode='edge')

    for i in range(len(data)-HISTORY_SIZE):
        subset_data = data[i:i+HISTORY_SIZE]
        lab_i = lab[i]
        X_train.append(subset_data)
        Y_train.append(lab_i)

X_train = np.float32(X_train)
Y_train = np.float32(Y_train)

model = Classifier()

def loss(y_true, y_pred):
    return -tf.reduce_mean(y_true * tf.math.log(y_pred * 0.99999 + 0.00001))

model.compile(optimizer='adam', loss=loss, metrics=['accuracy'])
model.fit(X_train, Y_train, epochs=50, batch_size=256)
model.save("model.h5", include_optimizer=False)

