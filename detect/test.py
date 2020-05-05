import csv
import glob
import time

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from model import predict, HISTORY_SIZE
from signal_proc import signoise, local_spectrum, restore_signal_from_local_spectrum

model = tf.keras.models.load_model("model.h5")

for filename in glob.glob("../data/smile10/*.csv"):
    with open(filename, "rt") as f:
        reader = csv.reader(f)

        data = []
        for row in reader:
            if len(row) > 1:
                data.append(float(row[1]))
        data = np.float32(data)

    data_padded = np.pad(data, ((HISTORY_SIZE, 0)), mode='edge')

    predictions = []
    xs = []

    for i in range(0, len(data), 10):
        xs.append(i)
        subset_data = data_padded[i:i + HISTORY_SIZE]

        time0 = time.time()
        pred = predict(model, subset_data)
        print(time.time() - time0)

        predictions.append(pred)

    predictions = np.float32(predictions)
    xs = np.float32(xs)

    plt.plot(data, scaley=True)
    plt.plot(xs, predictions[:, 1] * 40000, scaley=True)
    plt.show()