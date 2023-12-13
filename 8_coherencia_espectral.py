import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import csd, welch

# Komando-lerro argumentuak parseatu
parser = argparse.ArgumentParser(description='Azelerometroen datuak prozesatu eta magnitude squared coherence kalkulatu.')
parser.add_argument('folder_paths', type=str, nargs=2, help='Bi seinaleen CSV fitxategiak gordetzeko karpeta-mutilen bideak')
args = parser.parse_args()

# Minimum seinale luzera hasieratu
min_length = float('inf')

# Kalkulazio-emaitzen zerrenda hasieratu
coherence_results = []

# Karpeta-mutilean iteratu eta seinaleak prozesatu
for folder_path in args.folder_paths:
    folder_name = os.path.basename(folder_path)
    csv_file_path = os.path.join(folder_path, 'IIS3DWB_ACC.csv')

    # Kargatu CSV fitxategia DataFrame-en
    df = pd.read_csv(csv_file_path)

    # Atera CSV fitxategiko lehenengo zutabea, denbora segundutan
    time_column = df.iloc[:, 0].to_numpy()

    # Kalkulatu lehen eta azken balioen arteko denbora-tartea
    time_interval = (time_column[-1] - time_column[0]) / len(time_column)

    # Azelerometroaren balioak atera (adibidez, Z ardatza)
    accel_z = df['A_z [mg]'].to_numpy()

    # Eguneratu minimum seinale luzera
    min_length = min(min_length, len(accel_z))

    # Gorde seinalea kalkulazio-emaitzen zerrendan
    coherence_results.append((folder_name, accel_z, time_interval))

# Ziurtatu guztiak direla luzera bera daukaten seinaleak (min_length)
coherence_results = [(name, signal[:min_length], interval) for name, signal, interval in coherence_results]

# Bi seinaleen arteko magnitude squared coherence kalkulatu
frequencies, magnitude_squared_coherence = csd(
    coherence_results[0][1],
    coherence_results[1][1],
    fs=1 / coherence_results[0][2],
    nperseg=min_length,
    return_onesided=False
)

# Bi seinaleen potentzia-espektra-dentsitateak (PSD) kalkulatu
freq_signal1, psd_signal1 = welch(coherence_results[0][1], fs=1 / coherence_results[0][2], nperseg=min_length, return_onesided=False)
freq_signal2, psd_signal2 = welch(coherence_results[1][1], fs=1 / coherence_results[1][2], nperseg=min_length, return_onesided=False)

# PSD-ak erabiliz magnitude squared coherence kalkulatu
magnitude_squared_coherence /= (psd_signal1 * psd_signal2)

# Azpiseinaleak sortu

fig, axs = plt.subplots(3, 1, figsize=(12, 10))

# Segundoan denbora-ikur baten bektorea sortu
signal_length = min_length
time_vector = np.arange(signal_length) * coherence_results[0][2]

# Top segundoko seinaleak marraztu
for name, signal, _ in coherence_results:
    axs[0].plot(time_vector, signal[:min_length], label=name)
axs[0].set_title('Denbora-Arloko Seinaleak')
axs[0].set_xlabel('Denbora [s]')
axs[0].legend()

# Magnitude squared coherence erdiko segundoko seinalean marraztu
frequencies_csd = np.fft.fftfreq(signal_length, 1 / (1 / coherence_results[0][2]))  # Aldaketa lerro honetan
positive_frequencies_csd = frequencies_csd[frequencies_csd >= 0]  # Soilik balio positiboak
positive_magnitude_squared_coherence = np.abs(magnitude_squared_coherence[frequencies_csd >= 0])
axs[1].semilogy(positive_frequencies_csd[positive_frequencies_csd <= 5000], 1/(positive_magnitude_squared_coherence[positive_frequencies_csd <= 5000])/max(1/(positive_magnitude_squared_coherence[positive_frequencies_csd <= 5000])), label='Magnitude Squared Coherence')
axs[1].set_title('Magnitude Squared Coherence')
axs[1].set_xlabel('Frekuentzia [Hz]')
axs[1].set_xlim(0, 50)  # 5000 Hz-raino mugatu
axs[1].grid(True)

# Seinaleen FFT kalkulatu
fft_signal1 = np.abs(np.fft.fft(coherence_results[0][1]))
fft_signal2 = np.abs(np.fft.fft(coherence_results[1][1]))
frequencies_fft = np.fft.fftfreq(signal_length, 1 / (1 / coherence_results[0][2]))  # Aldaketa lerro honetan
positive_frequencies_fft = frequencies_fft[frequencies_fft >= 0]  # Soilik balio positiboak
axs[2].semilogy(positive_frequencies_fft[positive_frequencies_fft <= 5000], fft_signal1[frequencies_fft >= 0][positive_frequencies_fft <= 5000], label=f'FFT {coherence_results[0][0]}')
axs[2].semilogy(positive_frequencies_fft[positive_frequencies_fft <= 5000], fft_signal2[frequencies_fft >= 0][positive_frequencies_fft <= 5000], label=f'FFT {coherence_results[1][0]}')
axs[2].set_title('Seinaleen FFT')
axs[2].set_xlabel('Frekuentzia [Hz]')
axs[2].set_xlim(0, 50)  # 5000 Hz-raino mugatu
axs[2].legend()

# Magnitude squared coherence-ren balio maximoa eta hori dagokion frekuentzia lortu
max_magnitude_squared_coherence = min(positive_magnitude_squared_coherence[positive_frequencies_csd <= 50])
freq_at_max_coherence = positive_frequencies_csd[positive_magnitude_squared_coherence == max_magnitude_squared_coherence]

# Pantailan inprimatu
print(f'Max Magnitude Squared Coherence: {max_magnitude_squared_coherence:.2f} at Frequency: {freq_at_max_coherence[0]:.2f} Hz')

# Grafikoa erakutsi
plt.tight_layout()
plt.show()

# Grafiko-leihoa ixten baino lehen erakutsi esperimentazio-tasa (fs)
fs = 1 / coherence_results[0][2]
print(f'Esperimentazio-Tasa (fs): {fs:.2f} Hz')
