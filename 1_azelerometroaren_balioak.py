import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

# CSV fitxategia DataFrame-era kargatu
df = pd.read_csv('IIS3DWB_ACC.csv')

# Denbora eta azelerometroaren balioak atera
time = df['Time']
accel_x = df['A_x [mg]'].to_numpy()  # NumPy array-ra bihurtu
accel_y = df['A_y [mg]'].to_numpy()  # NumPy array-ra bihurtu
accel_z = df['A_z [mg]'].to_numpy()  # NumPy array-ra bihurtu

# Azelerometroaren balioen FFT-a kalkulatu
fft_x = np.abs(fft(accel_x))
fft_y = np.abs(fft(accel_y))
fft_z = np.abs(fft(accel_z))

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
freq = np.fft.fftfreq(len(time), d=(time[1] - time[0]))
plt.semilogy(freq, np.log10(fft_x), label='X-ardatza', linewidth=1)
plt.semilogy(freq, np.log10(fft_y), label='Y-ardatza', linewidth=1)
plt.semilogy(freq, np.log10(fft_z), label='Z-ardatza', linewidth=1)
plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Logaritmikoa Amplitudina')
plt.legend()

plt.tight_layout()
plt.show()
