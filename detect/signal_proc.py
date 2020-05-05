import tensorflow as tf
import numpy as np


WSIZE = 50
FREQ_LOW=0
FREQ_HIGH=0.2

window = tf.constant(np.cos(np.linspace(-np.pi/2, np.pi/2, WSIZE)), dtype=tf.float32)

mask = np.ones(WSIZE, dtype=np.complex)
mask[:int(WSIZE // 2 * FREQ_LOW)] = 0
mask[int(WSIZE // 2 * FREQ_HIGH):] = 0
mask[WSIZE // 2 + 1:] = mask[::-1][WSIZE // 2:-1]
mask = tf.constant(mask, dtype=tf.complex64)

sigma = 3
m = (WSIZE - 1)/2
i = np.linspace(0, WSIZE-1, WSIZE)
gaussian = np.exp(-(i-m)*(i-m)/(2*sigma*sigma))
gaussian /= sum(gaussian)
gaussian = tf.constant(gaussian, dtype=tf.float32)

# @tf.function
def local_spectrum(data, wsize):
    subsets = tf.stack([tf.roll(data, wsize//2 - i, axis=-2) for i in range(wsize)], axis=-1)
    subsets *= window
    subsets = tf.cast(subsets, tf.complex64)
    spectrum = tf.signal.fft(subsets)
    return spectrum

# @tf.function
def restore_signal_from_local_spectrum(local_spectrum_all):
    signal:tf.Tensor = tf.signal.ifft(local_spectrum_all)
    signal = tf.math.real(signal)
    signal = tf.reduce_sum(signal * gaussian, axis=-1)
    return signal

# @tf.function
def signoise(data):
    spec = local_spectrum(data, WSIZE)
    noise = spec[:, :, int(WSIZE // 2 * FREQ_HIGH):WSIZE // 2]
    noise = tf.reduce_mean(tf.abs(noise), axis=-1)

    spec *= mask

    data2 = restore_signal_from_local_spectrum(spec)

    return data2, noise