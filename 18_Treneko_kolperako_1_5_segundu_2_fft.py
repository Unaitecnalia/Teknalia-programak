import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import correlate
from scipy import exp

def find_peaks_custom(fft_data, side_distance=5):
    max_value = np.max(fft_data)
    threshold = np.mean(fft_data) * 3

    # fft_data-ren gainetik dagoen lekuan eta gailurra den tokian indices aurkitu
    peaks = []
    for i in range(side_distance, len(fft_data) - side_distance):
        if fft_data[i] > threshold and \
           all(fft_data[i] > fft_data[i-j] for j in range(1, side_distance + 1)) and \
           all(fft_data[i] > fft_data[i+j] for j in range(1, side_distance + 1)):
            peaks.append(i)

    return np.array(peaks)

# Komando lerroko argumentuak prozesatu
parser = argparse.ArgumentParser(description='Azelerometroaren datuak prozesatu eta irudikatu.')
parser.add_argument('folder_path', type=str, help='CSV fitxategiaren karpeta')
parser.add_argument('--max_frequency', type=float, default=5000, help='FFT irudirako gehienezko frekuentzia (Hz)')
parser.add_argument('--threshold', type=float, default=2000, help='Hasierako puntuaren detektatzeko tartea')
args = parser.parse_args()

# CSV fitxategiaren bidea karpeta batera bildu
folder_name = os.path.basename(args.folder_path)
csv_file_path = os.path.join(args.folder_path, 'IIS3DWB_ACC.csv')

# CSV fitxategia DataFrame bihurtu
df = pd.read_csv(csv_file_path)

# Denbora, azelerometro balioak (X, Y, Z) atera
time = df['Time']
accel_x = df['A_x [mg]'].to_numpy()
accel_y = df['A_y [mg]'].to_numpy()
accel_z = df['A_z [mg]'].to_numpy()

# Hasierako puntuaren detektatzeko erabiliko den tartea kalkulatu
start_index = np.argmax(np.abs(accel_x) > args.threshold)

# Hurrengo 1.5 segundoetako datuak atera
fps = 1 / (time[1] - time[0])
start_index = max(0, start_index - int(0.15 * fps))
end_index = start_index + int(1.35 * fps) 

# X, Y, eta Z-aren datuak erakusteko denbora domeinuko irudiak sortu
plt.figure(figsize=(12, 8))  # Altura handitu bi subplotentzako

# Ajustatutako y-ardatzeko azelerometro datuak erakutsi
plt.subplot(3, 1, 1)  # Hiru lerro, zutabe bat, lehenengo subplota
plt.plot(time[start_index:end_index], accel_x[start_index:end_index], label='X ardatza')

plt.xlabel('Denbora')
plt.ylabel('Azelerazioa [mg]')
plt.title('Azelerazio Datuak (X, Y, eta Z) 1.5 Segundutara')
plt.grid(True)
plt.legend()
plt.ylim(-1500, 1500)  # Ajustatutako y-ardatzeko muga

# Hautatutako datuen FFTa (lineal eskala) kalkulatu eta erakutsi
plt.subplot(2, 2, 3)  # Hiru lerro, bi zutabe, bigarren subplota (lineal eskala)
N = len(time[start_index:end_index])
sampling_rate = 1 / (time[start_index + 1] - time[start_index])
freq = fftfreq(N, 1 / sampling_rate)
positive_freq_indices = np.where((freq >= 0) & (freq <= args.max_frequency))
freq = freq[positive_freq_indices]
fft_x = np.abs(fft(accel_x[start_index:end_index]))[positive_freq_indices]

# 20 Hz edo gehiago duten frekuentzietan kokatutako indizea identifikatu
index_20hz = np.argmax(freq >= 20)

# fft_x, fft_y, eta fft_z matrizeen eremuetan gehieneko balioa identifikatu
max_value_x = np.max(fft_x[index_20hz:])

# max_value kalkulatu, gehieneko balioen artean gehienez 1.2 bideratuz
max_value = 1.2 * max_value_x

# fft1-entzako pikoak aurkitu eta erakutsi
peaks1 = find_peaks_custom(fft_x, side_distance=400)
print(peaks1)

# fft1-entzako pikak erakusteko anotazioak
for peak in peaks1:
    plt.annotate(f'{freq[peak]:.2f} Hz', (freq[peak], fft_x[peak]),
                textcoords="offset points", xytext=(0, 10), ha='center')

# FFT erakutsi kalkulatutako max_value-arekin eta y-ardatzeko muga ajustatu (lineal eskala)
plt.plot(freq, fft_x, label='X ardatza')

plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Lineal Amplitud')
plt.ylim(0, max_value)  # Ajustatutako y-ardatzeko muga
plt.title('Hautatutako Datuen FFTa (X, Y, eta Z)')
plt.grid(True)
plt.legend()

# Hautatutako datuen FFTa (logaritmikoa) kalkulatu eta erakutsi
plt.subplot(2, 2, 4)  # Hiru lerro, bi zutabe, hirugarren subplota (logaritmikoa)

# FFT emaitzak erabiliz, baina logaritmikoa erabiliz erakutsi
plt.plot(freq, 20 * np.log10(fft_x), label='X ardatza')

plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Logaritmikoa Amplitudua (dB)')
plt.title('Hautatutako Datuen FFTa Logaritmikoa (X, Y, eta Z)')
plt.grid(True)
plt.legend()

# Irudiak gorde
output_image_path = os.path.join(args.folder_path, 'konparazioa_' + folder_name + '.png')
plt.savefig(output_image_path)
print('Gordeta: ' + output_image_path)

# Hautatutako datuak CSV fitxategian gorde
# selected_data = df.iloc[start_index:end_index]
# output_csv_path = os.path.join(args.folder_path, folder_name + '.csv')
# selected_data.to_csv(output_csv_path, index=False)

# Irudiak erakutsi
# plt.tight_layout()
# plt.show()
