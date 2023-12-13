import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import correlate
from scipy import exp

# Komando-lerro argumentuak parseatu
parser = argparse.ArgumentParser(description='Azelerometroen datuak prozesatu eta irudikatu.')
parser.add_argument('folder_path', type=str, help='CSV fitxategiaren karpeta-muturra')
parser.add_argument('--max_frequency', type=float, default=5000, help='Gehienezko frekuentzia (Hz) FFT irudikapenarako')
parser.add_argument('--threshold', type=float, default=2000, help='Hasi-puntu detektatzeko tamaina')
args = parser.parse_args()

# CSV fitxategiaren bidea lortu karpeta-mutilaren bideaz
folder_name = os.path.basename(args.folder_path)
csv_file_path = os.path.join(args.folder_path, 'IIS3DWB_ACC.csv')

# Kargatu CSV fitxategia DataFrame-en
df = pd.read_csv(csv_file_path)

# Atera denbora eta azelerometroaren balioak (X, Y, Z)
time = df['Time']
accel_x = df['A_x [mg]'].to_numpy()
accel_y = df['A_y [mg]'].to_numpy()
accel_z = df['A_z [mg]'].to_numpy()

# Hasi-puntua detektatu tamaina erabiliz
start_index = np.argmax(np.abs(accel_x) > args.threshold)

# Atera hurrengo 1.5 segundoetako datuak
fps = 1 / (time[1] - time[0])
start_index = max(0, start_index - int(0.15 * fps))
end_index = start_index + int(1.35 * fps)  # Luzatu 1.5 segundoetara

# Sortu denbora-ikurra X, Y eta Z arloentzat
plt.figure(figsize=(12, 6))

# Azelerometroaren datuak erakutsi, y-ardatzaren mugak egokitu eta ikurraren eta FFT-ren plot egin
plt.subplot(2, 1, 1)
plt.plot(time[start_index:end_index], accel_x[start_index:end_index], label='X-ardatza')
plt.plot(time[start_index:end_index], accel_y[start_index:end_index], label='Y-ardatza')
plt.plot(time[start_index:end_index], accel_z[start_index:end_index], label='Z-ardatza')
plt.xlabel('Denbora')
plt.ylabel('Azelerazioa [mg]')
plt.title('Azelerazio Datuen 1.5 Segunduak (X, Y, eta Z)')
plt.grid(True)
plt.legend()
plt.ylim(-1500, 1500)  # Egokitu y-ardatzaren mugak

# Kalkulatu eta plot egin FFT aukeratutako datuetarako
plt.subplot(2, 1, 2)
N = len(time[start_index:end_index])
muestreo_frekuentzia = 1 / (time[start_index + 1] - time[start_index])
freq = fftfreq(N, 1 / muestreo_frekuentzia)
positibo_freq_indizeak = np.where((freq >= 0) & (freq <= args.max_frequency))
freq = freq[positibo_freq_indizeak]
fft_x = np.abs(fft(accel_x[start_index:end_index]))[positibo_freq_indizeak]
fft_y = np.abs(fft(accel_y[start_index:end_index]))[positibo_freq_indizeak]
fft_z = np.abs(fft(accel_z[start_index:end_index]))[positibo_freq_indizeak]

# Kalkulatu max_value FFT balioen batez besteko gisa
max_value = (np.mean(fft_x) + np.mean(fft_y) + np.mean(fft_z)) / 3.0

# FFT-ren autocorrelation kalkulatu exponetzialaren funtzioarekin
korrelazioa = correlate(fft_x, exp(-np.arange(len(fft_x))))
emaitza = korrelazioa.max()

# max_value banatu autocorrelation emaitzarekin
max_value /= emaitza
max_value *= 1500000000

# Plot egin FFT-arekin kalkulatutako max_value-arekin eta erabilgarritasun egokitutako y-ardatzaren mugak
plt.plot(freq, fft_x, label='X-ardatza')
plt.plot(freq, fft_y, label='Y-ardatza')
plt.plot(freq, fft_z, label='Z-ardatza')
plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Lineal Amplituduna')
plt.ylim(0, max_value)  # Egokitu y-ardatzaren mugak
plt.title('Aukeratutako Datuen FFT-a (X, Y, eta Z)')
plt.grid(True)
plt.legend()

# Irudiaren bidea irudikatzaile gisa gorde
irudiaren_bidea = os.path.join(args.folder_path, folder_name + '.png')
plt.savefig(irudiaren_bidea)

# Hautatutako datuak CSV fitxategi gisa gorde
hautatutako_datuak = df.iloc[start_index:end_index]
csv_bidea = os.path.join(args.folder_path, folder_name + '.csv')
hautatutako_datuak.to_csv(csv_bidea, index=False)

# Plot erakutsi
plt.tight_layout()
plt.show()
