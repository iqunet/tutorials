
import numpy as np
import matplotlib.pyplot as plt

# Parameters
Fs = 50000  # Higher sampling frequency for more detail
T = 1.0 / Fs  # Sampling interval
L = 10000  # Length of signal
t = np.arange(0, L) * T  # Time vector

# Fundamental frequency
f1 = 50  # 50Hz fundamental frequency

# Harmonic frequencies
f5 = 5 * f1  # 5th harmonic
f7 = 7 * f1  # 7th harmonic

# Amplitudes of the signals
A1 = 1.0  # Amplitude of fundamental
A5 = -0.3  # Amplitude of 5th harmonic
A7 = 0.1  # Amplitude of 7th harmonic

# Sine wave and harmonics
y1 = A1 * np.sin(2 * np.pi * f1 * t)
y5 = A5 * np.sin(2 * np.pi * f5 * t)
y7 = A7 * np.sin(2 * np.pi * f7 * t)

# Combined signal
y = y1 + y5 + y7

# FFT
Y = np.fft.fft(y)
P2 = np.abs(Y / L)
P1 = P2[:L // 2 + 1]
P1[1:-1] = 2 * P1[1:-1]
f = Fs * np.arange((L // 2) + 1) / L

# Plotting
plt.figure(figsize=(5, 3))

# Time domain plot
plt.subplot(2, 1, 1)
plt.plot(t, y, label='Combined Signal', color='b', alpha=0.7)
plt.title('Time Domain Signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.xlim([0, 0.1])
plt.legend()

# Frequency domain plot with bars
plt.subplot(2, 1, 2)
plt.bar(f, P1, width=20, label='Magnitude Spectrum', color='r', alpha=0.7)
plt.title('Frequency Domain Signal')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim([0, 500])
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()

plt.tight_layout()
plt.show()
