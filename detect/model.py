from signal_proc import signoise, local_spectrum, restore_signal_from_local_spectrum
import tensorflow as tf
import numpy as np

HISTORY_SIZE = 64

def Classifier(HISTORY_SIZE=HISTORY_SIZE, CHANNELS=1, EMOTIONS=1, HIDDEN_SIZE=16) -> tf.keras.Model:
    input = tf.keras.layers.Input((HISTORY_SIZE, CHANNELS))
    x = input

    signal, noise = tf.keras.layers.Lambda(signoise)(x)
    x = tf.keras.layers.Concatenate()([signal, noise])

    N_LAYERS = int(np.log2(HISTORY_SIZE))
    for i in range(N_LAYERS):
        x = tf.keras.layers.Conv1D(HIDDEN_SIZE, 7, strides=2, padding='same')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation('tanh')(x)

    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(EMOTIONS+1, activation='softmax')(x)

    return tf.keras.models.Model(inputs=input, outputs=x)

@tf.function
def predict(model, data):
    data = tf.expand_dims(data, axis=0)
    data = tf.expand_dims(data, axis=-1)
    pred = model(data)
    return pred[0]