import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import butter, sosfreqz, sosfilt

# Komando-lerro argumentuak parseatu
parser = argparse.ArgumentParser(description='Azelerometroen datuak prozesatu eta irudikatu.')
parser.add_argument('folder_paths', type=str, nargs='+', help='CSV fitxategiak gordetzeko karpeta-mutilen bideak')
args = parser.parse_args()

# Z filtroaren parametroak zehaztu
lowcut = 0.1  
highcut = 20.0
fs = 100.0

# Kalkulatu filtroaren koefizienteak
sos = butter(4, [lowcut, highcut], btype='band', fs=fs, output='sos')

# FFT emaitzen luzera minimoa aurkitu
min_length = float('inf')

# Prozesatu mapaketa bakoitza eta kalkulatu FFT emaitzak
fft_emaitzak = []

# Gorde energia txikiena
min_energia = float('inf')

for folder_path in args.folder_paths:
    # Karpeta-mutiletik hartu CSV fitxategiaren bidea
    folder_name = os.path.basename(folder_path)
    csv_file_path = os.path.join(folder_path, 'IIS3DWB_ACC.csv')

    # Kargatu CSV fitxategia DataFrame-en
    df = pd.read_csv(csv_file_path)

    # Azelerometroaren balioak atera (Z ardatza)
    accel_z = df['A_z [mg]'].to_numpy()

    # Bandpasa-filtroa aplikatu seinaleari
    iragazitutako_seinalea = sosfilt(sos, accel_z)

    # Kalkulatu iragazitutako seinalearen FFT-a
    N = len(iragazitutako_seinalea)
    freq = fftfreq(N, 1 / fs)
    positive_freq_indices = np.where((freq >= 0) & (freq <= highcut))

    # Zehaztu zenbat frekuentzia-puntu erakutsi nahi diren (adibidez, 100 puntu)
    erakutsi_nahi_diren_puntu_kopurua = 100
    urratsa = len(positive_freq_indices[0]) // erakutsi_nahi_diren_puntu_kopurua
    aukeratutako_freq_indizeak = positive_freq_indices[0][::urratsa]

    freq = freq[aukeratutako_freq_indizeak]
    fft_z = np.abs(fft(iragazitutako_seinalea))[aukeratutako_freq_indizeak]

    # Energiaren kalkulua
    energia = np.sum(np.abs(fft_z) ** 2)

    # Gorde energia txikiena
    min_energia = min(min_energia, energia)

    # Gorde FFT emaitzak
    fft_emaitzak.append((folder_name, freq, fft_z, energia))

    # Eguneratu FFT emaitzen luzera minimoa
    min_length = min(min_length, len(freq))

# Energiak normalizatu, energia txikienarekin bananduz
normalizatutako_fft_emaitzak = []

for folder_name, freq, fft_z, energia in fft_emaitzak:
    normalizatutako_energia = energia / min_energia
    normalizatutako_fft_emaitzak.append((folder_name, freq, fft_z, normalizatutako_energia))

# Inprimatu FFT multzoaren luzera eta normalizatutako energia maparen bakoitzean
for folder_name, _, _, normalizatutako_energia in normalizatutako_fft_emaitzak:
    print(f'{folder_name}: FFT multzoaren luzera = {min_length}, Normalizatutako Energia = {normalizatutako_energia:.2f}')

# Trunkatu edo zero-padditu FFT emaitzak luzera berdina izateko (min_length)
prozesatuak_fft_emaitzak = []

for folder_name, freq, fft_z, energia in normalizatutako_fft_emaitzak:
    if len(freq) < min_length:
        # Zero-padatu FFT emaitza luzerak baino motza baldin bada
        fft_z = np.pad(fft_z, (0, min_length - len(freq)))

    prozesatuak_fft_emaitzak.append((folder_name, freq, fft_z, energia))

# X, Y eta Z arloetarako denbora-ikurra sortu
plt.figure(figsize=(12, 8))

# Logaritmikoa denbora-ikurra erakutsi mapako bakoitzean
for folder_name, freq, fft_z, energia in prozesatuak_fft_emaitzak:
    plt.semilogy(freq, fft_z, label=f'{folder_name}, Normalizatutako Energia = {energia:.2f}')

plt.xlabel('Frekuentzia [Hz]')
plt.ylabel('Logaritmikoa Amplituduna')
plt.title('FFT Emaitzen Alderaketa (Z-arloa) Logaritmikoan')
plt.grid(True)
plt.legend()

# Grafikoa erakutsi
plt.tight_layout()
plt.show()
