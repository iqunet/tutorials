
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Parameters
Fs = 50000  # Sampling frequency
T = 1.0 / Fs  # Sampling interval
L = 1000  # Length of signal
t = np.arange(0, L) * T  # Time vector
f1 = 50  # Fundamental frequency
phi = - np.pi / 4  # Phase shift for displacement power factor

# Generating signals
# Case 1: Pure sinusoidal with PF = 1
V1 = np.sin(2 * np.pi * f1 * t)
I1 = np.sin(2 * np.pi * f1 * t)

# Case 2: Sinusoidal with displacement power factor
I2 = np.sin(2 * np.pi * f1 * t + phi)

# Case 3: Sinusoidal with harmonics, PF = 1
I3 = np.sin(2 * np.pi * f1 * t) - 0.3 * np.sin(2 * np.pi * 5 * f1 * t) + 0.1 * np.sin(2 * np.pi * 7 * f1 * t)

# Case 4: Sinusoidal with harmonics and displacement power factor
I4 = np.sin(2 * np.pi * f1 * t + phi) - 0.3 * np.sin(2 * np.pi * 5 * f1 * t + phi) + 0.1 * np.sin(2 * np.pi * 7 * f1 * t + phi)

# FFT function
def fft_magnitude(signal):
    Y = np.fft.fft(signal)
    P2 = np.abs(Y / L)
    P1 = P2[:L // 2 + 1]
    P1[1:-1] = 2 * P1[1:-1]
    f = Fs * np.arange((L // 2) + 1) / L
    return f, P1

# THD calculation
def calculate_thd(signal):
    _, P1 = fft_magnitude(signal)
    fundamental = P1[1]
    harmonics = np.sqrt(np.sum(P1[2:]**2))
    thd = harmonics / fundamental
    return thd

# Plotting
fig, axs = plt.subplots(4, 2, figsize=(8, 6))
plt.style.use('dark_background')  # Set background to black

# Set background color for the figure and subplots
fig.patch.set_facecolor('black')
for ax in axs.flatten():
    ax.set_facecolor('black')

# Time domain plots
axs[0, 0].plot(t, V1, label='Voltage', color='yellow')
axs[0, 0].plot(t, 0.1+I1, label='Current', color='magenta')
axs[0, 0].set_title(f'cos($\\phi$) = 1 / THDi = {calculate_thd(I1):.0%}', color='yellow')
axs[0, 0].set_xlim([0, 0.02])
axs[0, 0].grid(True, color='gray')
axs[0, 0].legend(fontsize='small', loc='upper right')
axs[0, 0].text(0.001, -0.9, 'Pure sinusoidal', fontsize=12, color='white', ha='left', va='bottom', fontname='monospace')

axs[1, 0].plot(t, V1, label='Voltage', color='yellow')
axs[1, 0].plot(t, I2, label='Current', color='magenta')
axs[1, 0].set_title(f'cos($\\phi$) = {np.cos(phi):.2f} / THDi = {calculate_thd(I2):.0%}', color='yellow')
axs[1, 0].set_xlim([0, 0.02])
axs[1, 0].grid(True, color='gray')
axs[1, 0].legend(fontsize='small', loc='upper right')
axs[1, 0].text(0.001, -0.9, 'Phase lagging', fontsize=12, color='white', ha='left', va='bottom', fontname='monospace')

axs[2, 0].plot(t, V1, label='Voltage', color='yellow')
axs[2, 0].plot(t, I3, label='Current', color='magenta')
axs[2, 0].set_title(f'cos($\\phi$) = 1 / THDi = {calculate_thd(I3):.0%}', color='yellow')
axs[2, 0].set_xlim([0, 0.02])
axs[2, 0].grid(True, color='gray')
axs[2, 0].legend(fontsize='small', loc='upper right')
axs[2, 0].text(0.001, -0.9, 'Distortion', fontsize=12, color='white', ha='left', va='bottom', fontname='monospace')

axs[3, 0].plot(t, V1, label='Voltage', color='yellow')
axs[3, 0].plot(t, I4, label='Current', color='magenta')
axs[3, 0].set_title(f'cos($\\phi$) = {np.cos(phi):.2f} / THDi = {calculate_thd(I4):.0%}', color='yellow')
axs[3, 0].set_xlim([0, 0.02])
axs[3, 0].grid(True, color='gray')
axs[3, 0].legend(fontsize='small', loc='upper right')

# Add black rectangle and text for 'Lagging & Distortion'
rect = patches.Rectangle((0.001, -1.4), 0.01, 0.4, linewidth=0, edgecolor='none', facecolor='black', zorder=1)
axs[3, 0].add_patch(rect)
axs[3, 0].text(0.001, -1.2, 'Lagging & Distortion', fontsize=12, color='white', ha='left', va='bottom', fontname='monospace', zorder=2, bbox=dict(facecolor='black', alpha=0.9, edgecolor='black'))

# Frequency domain plots
def plot_harmonics(ax, f, P1, title):
    ax.bar(f, P1, width=8.5, color='magenta', alpha=0.7, label='Current')
    ax.bar(f, fft_magnitude(V1)[1], width=3.5, color='yellow', alpha=0.7, label='Voltage')
    ax.set_xlim([0, 500])
    ax.set_title(title, color='yellow')
    ax.grid(True, color='gray')
    ax.legend(fontsize='small', loc='upper right')
    # Mark 5th and 7th harmonics
    ax.plot(5*f1, P1[5*f1*L//Fs], 'y^')
    ax.text(5*f1, P1[5*f1*L//Fs], '5th', color='yellow', ha='left', va='bottom', fontname='monospace')
    ax.plot(7*f1, P1[7*f1*L//Fs], 'y^')
    ax.text(7*f1, P1[7*f1*L//Fs], '7th', color='yellow', ha='left', va='bottom', fontname='monospace')

f, P1 = fft_magnitude(I1)
plot_harmonics(axs[0, 1], f, P1, 'PF = 1')

f, P2 = fft_magnitude(I2)
plot_harmonics(axs[1, 1], f, P2, 'DispF')

f, P3 = fft_magnitude(I3)
plot_harmonics(axs[2, 1], f, P3, 'DistF')

f, P4 = fft_magnitude(I4)
plot_harmonics(axs[3, 1], f, P4, 'DispF & DistF')

# Adjust grid lines and axes colors
for ax in axs.flatten():
    ax.xaxis.label.set_color('yellow')
    ax.yaxis.label.set_color('yellow')
    ax.tick_params(axis='x', colors='yellow')
    ax.tick_params(axis='y', colors='yellow')
    ax.spines['bottom'].set_color('yellow')
    ax.spines['top'].set_color('yellow')
    ax.spines['left'].set_color('yellow')
    ax.spines['right'].set_color('yellow')

for ax in axs[:, 0]:
    ax.set_xticklabels([])

# Final adjustments
plt.tight_layout()
plt.show()
