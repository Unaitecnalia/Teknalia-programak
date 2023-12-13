import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks, correlate
from scipy import exp
import datetime
import shutil
from adjustText import adjust_text

# Komando-lerro argumentuak parseatu
parser = argparse.ArgumentParser(description='Azelerometroen datuak prozesatu eta irudikatu.')
parser.add_argument('folder_path', type=str, help='CSV fitxategiaren karpeta-muturra')
parser.add_argument('--max_frequency', type=float, default=5000, help='Gehienezko frekuentzia (Hz) FFT irudikapenarako')
parser.add_argument('--start_time', type=float, default=None, help='Hasierako denbora segundoetan (lehenetsia: None)')
parser.add_argument('--end_time', type=float, default=None, help='Bukaerako denbora segundoetan (lehenetsia: None)')
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
start_index = max(0, start_index + int(0.05 * fps))
end_index = start_index + int(0.55 * fps)  # Luzatu 1.5 segundoetara

# Sortu denbora-ikurra X, Y eta Z arloentzat
plt.figure(figsize=(12, 8))  # Altuera handitu bi azpimarrapeneentzat

# Azelerometroaren datuak erakutsi, y-ardatzaren mugak egokitu eta ikurraren eta FFT-ren plot egin
plt.subplot(3, 1, 1)  # Hiru errenkadak, bat zutabe, lehenengo subplota
plt.plot(time[start_index:end_index], accel_x[start_index:end_index], label='X-ardatza')
plt.plot(time[start_index:end_index], accel_y[start_index:end_index], label='Y-ardatza')
plt.plot(time[start_index:end_index], accel_z[start_index:end_index], label='Z-ardatza')
plt.xlabel('Denbora')
plt.ylabel('Azelerazioa [mg]')
plt.title('Azelerazio Datuen 1.5 Segunduak (X, Y, eta Z)')
plt.grid(True)
plt.legend()
plt.ylim(-1500, 1500)  # Egokitu y-ardatzaren mugak

# Kalkulatu eta plot egin FFT aukeratutako datuetarako (lineal graduan)
plt.subplot(2, 2, 3)  # Hiru errenkadak, bi zutabe, bigarren subplota (lineal graduan)
N = len(time[start_index:end_index])
muestreo_frekuentzia = 1 / (time[start_index + 1] - time[start_index])
freq = fftfreq(N, 1 / muestreo_frekuentzia)
positibo_freq_indizeak = np.where((freq >= 0) & (freq <= args.max_frequency))
freq = freq[positibo_freq_indizeak]
fft_x = np.abs(fft(accel_x[start_index:end_index]))[positibo_freq_indizeak]
fft_y = np.abs(fft(accel_y[start_index:end_index]))[positibo_freq_indizeak]
fft_z = np.abs(fft(accel_z[start_index:end_index]))[positibo_freq_indizeak]

# 20 Hz eta 50 Hz artean den frekuentzia-indizea identifikatu
index_10hz = np.argmax(freq >= 20)

# fft_x, fft_y eta fft_z matrizeen alde erabilgarrietakoak diren parteen artean maximoa lortu
max_value_x = np.max(fft_x[index_10hz:])
max_value_y = np.max(fft_y[index_10hz:])
max_value_z = np.max(fft_z[index_10hz:])

# max_value kalkulatu maximoen bikoitzaren bidez
max_value = 1.2 * max(max_value_x, max_value_y, max_value_z)

# Plot egin FFT-arekin max_value kalkulatua eta egokitu y-ardatzaren mugak (lineal graduan)
plt.plot(freq, fft_x, label='X-ardatza')
plt.plot(freq, fft_y, label='Y-ardatza')
plt.plot(freq, fft_z, label='Z-ardatza')
plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Lineal Amplituduna')
plt.ylim(0, max_value)  # Egokitu y-ardatzaren mugak
plt.title('FFT Aukeratutako Datuetarako (X, Y, eta Z)')
plt.grid(True)
plt.legend()

# Pikoak bilatu FFTn, iragan hainbat eta mirail batzuekin
pikoak, _ = find_peaks(fft_z, height=None)

# Pikoak ezabatu 5 balioen ezkerretik eta 5 eskubirik baino handiagoak direnak
piko_bilaketa_neurria = int(2 * len(fft_z) / 35)  # Zortziaren erdiakoa pikoak bilatzeko neurria

pikoak_hobetuak = []
for piko in pikoak:
    if (
        piko >= piko_bilaketa_neurria and piko <= len(fft_z) - piko_bilaketa_neurria - 1 and
        all(fft_z[piko] > fft_z[piko - i] for i in range(1, piko_bilaketa_neurria + 1)) and
        all(fft_z[piko] > fft_z[piko + i] for i in range(1, piko_bilaketa_neurria + 1))
    ):
        pikoak_hobetuak.append(piko)

print("\nPikoak: ", pikoak_hobetuak)

# Pikoak dagokion frekuentziekin lortu
piko_frekuentziak = freq[pikoak_hobetuak]
print("Frekuentziak", piko_frekuentziak)

# Irudian piko frekuentziak etiketatzen hasi
irudiak = []
for frekuentzia, piko in zip(piko_frekuentziak, pikoak_hobetuak):
    y_posizioa = fft_z[piko]
    irudiak.append(plt.text(frekuentzia, y_posizioa, f'{frekuentzia:.2f} Hz', ha='center'))

# Etiketak arruntaketak saihesteko egokitzen ditu
adjust_text(irudiak, arrowprops=dict(arrowstyle='->', lw=0.5))

# Kalkulatu eta plot egin FFT aukeratutako datuetarako (logaritmikoan)
plt.subplot(2, 2, 4)  # Hiru errenkadak, bi zutabe, hirugarren subplota (logaritmikoan)

# Erabil ezazu FFT emaitzak baina plot egin logaritmikoan
plt.plot(freq, 20 * np.log10(fft_x), label='X-ardatza')
plt.plot(freq, 20 * np.log10(fft_y), label='Y-ardatza')
plt.plot(freq, 20 * np.log10(fft_z), label='Z-ardatza')
plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Logaritmikoa Amplituduna (dB)')
plt.title('FFT Aukeratutako Datuetarako Logaritmikoan (X, Y, eta Z)')
plt.grid(True)
plt.legend()

# Irudia irudikatzaile gisa gorde
irudia_bidea = os.path.join(args.folder_path, folder_name + '.png')
plt.savefig(irudia_bidea)

# Hautatutako datuak CSV fitxategi gisa gorde
hautatutako_datuak = df.iloc[start_index:end_index]
csv_bidea = os.path.join(args.folder_path, folder_name + '.csv')
hautatutako_datuak.to_csv(csv_bidea, index=False)

# Irudia erakutsi
# plt.tight_layout()
# plt.show()

# Une honetako data lortu
uneko_data = datetime.datetime.now().strftime("%Y%m%d")

# Une honetako karpeta-izena erabiliz
irudien_karpeta_izena = f"{uneko_data}_PNG"

# Irudiak gordeko diren karpeta-muturra
irudien_karpeta_bidea = os.path.join(os.getcwd(), irudien_karpeta_izena)

# Egiaztatu karpeta existitzen dela, eta ez badago, sortu
if not os.path.exists(irudien_karpeta_bidea):
    os.makedirs(irudien_karpeta_bidea)

# Irudiaren bidea irudien_karpeta_bidean
irudiak_bidean_une_honetan = os.path.join(irudien_karpeta_bidea, f'{folder_name}_{args.start_time}s_etatik_{args.end_time}s_6_programa.png')

# Irudia kopiatu irudiak_karpeta_bidean
shutil.copy(irudia_bidea, irudiak_bidean_une_honetan)

print("Gordeta: ", irudiak_bidean_une_honetan)
