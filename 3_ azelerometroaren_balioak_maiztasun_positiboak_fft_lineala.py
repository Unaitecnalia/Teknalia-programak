import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# Komando-lerro argumentuak parseatu
parser = argparse.ArgumentParser(description='Azelerometroaren datuak eta FFT-aren plot-ak egin.')
parser.add_argument('csv_file', type=str, help='Azelerometroaren datuak dituen CSV fitxategiaren bidea')
parser.add_argument('--max_value', type=float, default=0.1, help='FFT-aren Y-ardatzarako gehienezko balioa')
parser.add_argument('--max_frequency', type=float, default=100, help='Gehienezko frekuentzia (Hz) FFT-aren plot-entzat')
args = parser.parse_args()

# CSV fitxategia DataFrame-en kargatu
df = pd.read_csv(args.csv_file)

# Denbora eta azelerometroaren balioak atera
time = df['Time']
accel_x = df['A_x [mg]'].to_numpy()  # NumPy array-ra bihurtu
accel_y = df['A_y [mg]'].to_numpy()  # NumPy array-ra bihurtu
accel_z = df['A_z [mg]'].to_numpy()  # NumPy array-ra bihurtu

# Azelerometroaren balioen FFT-a kalkulatu
N = len(time)
muestreo_frekuentzia = 1 / (time[1] - time[0])
freq = fftfreq(N, 1 / muestreo_frekuentzia)
positibo_freq_indizeak = np.where((freq >= 0) & (freq <= args.max_frequency))
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

# FFT-aren plot-a sortu, erabiltzaileak zehaztutako Y balio maximoa erabiliz
plt.subplot(2, 1, 2)
plt.plot(freq, fft_x, label='X-ardatza', linewidth=1)
plt.plot(freq, fft_y, label='Y-ardatza', linewidth=1)
plt.plot(freq, fft_z, label='Z-ardatza', linewidth=1)
plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Lineal Amplitud')
plt.ylim(0, args.max_value)  # Erabiltzaileak sartutako Y balio maximoa ezarri
plt.legend()

plt.tight_layout()
plt.show()
