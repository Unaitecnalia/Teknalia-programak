import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# CSV fitxategia DataFrame-era kargatu
df = pd.read_csv('IIS3DWB_ACC.csv')

# Denbora eta azelerometroaren balioak atera
time = df['Time']
accel_x = df['A_x [mg]'].to_numpy()  # NumPy array-ra bihurtu
accel_y = df['A_y [mg]'].to_numpy()  # NumPy array-ra bihurtu
accel_z = df['A_z [mg]'].to_numpy()  # NumPy array-ra bihurtu

# Azelerometroaren balioen FFT-a kalkulatu
N = len(time)
muestreo_frekuentzia = 1 / (time[1] - time[0])
freq = fftfreq(N, 1 / muestreo_frekuentzia)
max_freq = 100  # Gehienezko frekuentzia 2000 Hz-koa ezartu
positibo_freq_indizeak = np.where((freq >= 0) & (freq <= max_freq))
freq = freq[positibo_freq_indizeak]
fft_x = np.abs(fft(accel_x))[positibo_freq_indizeak]
fft_y = np.abs(fft(accel_y))[positibo_freq_indizeak]
fft_z = np.abs(fft(accel_z))[positibo_freq_indizeak]

# Denborako plot-a sortu
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(time, accel_x, label='X-ardatza', linewidth=1)
plt.plot(time, accel_y, label='Y-ardatza', linewidth=1)
plt.plot(time, accel_z, label='Z-ardatza', linewidth=1)
plt.xlabel('Denbora')
plt.ylabel('Azelerazioa [mg]')
plt.legend()

# FFT-aren plot-a sortu, logaritmikoan
plt.subplot(2, 1, 2)
plt.semilogy(freq, np.log10(fft_x), label='X-ardatza', linewidth=1)
plt.semilogy(freq, np.log10(fft_y), label='Y-ardatza', linewidth=1)
plt.semilogy(freq, np.log10(fft_z), label='Z-ardatza', linewidth=1)
plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Logaritmikoa Amplitudina')
plt.legend()

plt.tight_layout()
plt.show()
