import argparse
import os
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import datetime

# Komando-lerro argumentuak parseatu
parser = argparse.ArgumentParser(description='Azelerometroaren datuak eta FFT-aren plot-ak egin.')
parser.add_argument('folder_paths', nargs='+', type=str, help='CSV fitxategiak dituen karpeta-muturrak')
parser.add_argument('--start_time', type=float, default=None, help='Hasiera denbora segundoetan (lehenetsia: None)')
parser.add_argument('--end_time', type=float, default=None, help='Amaiera denbora segundoetan (lehenetsia: None)')
parser.add_argument('--max_value', type=float, help='FFT-aren Y-ardatzarako gehienezko balioa')
parser.add_argument('--max_frequency', type=float, default=10000, help='Gehienezko frekuentzia (Hz) FFT-aren plot-entzat')
args = parser.parse_args()

for folder_path in args.folder_paths:
    # Karpeta-mutilaren bideaz CSV fitxategiaren bidea lortu
    folder_name = os.path.basename(folder_path)
    csv_file_path = os.path.join(folder_path, 'IIS3DWB_ACC.csv')

    # Kargatu CSV fitxategia DataFrame-en
    df = pd.read_csv(csv_file_path)

    # Atera denbora eta azelerometroaren balioak
    time = df['Time']
    accel_x = df['A_x [mg]'].to_numpy()  # NumPy array-ra bihurtu
    accel_y = df['A_y [mg]'].to_numpy()  # NumPy array-ra bihurtu
    accel_z = df['A_z [mg]'].to_numpy()  # NumPy array-ra bihurtu

    # Aplikatu denbora-arloa hasiera_denbora eta amaiera_denbora ematen bada
    if args.start_time is not None and args.end_time is not None:
        denbora_arloa_indizeak = (time >= args.start_time) & (time <= args.end_time)
        time = time[denbora_arloa_indizeak]
        accel_x = accel_x[denbora_arloa_indizeak]
        accel_y = accel_y[denbora_arloa_indizeak]
        accel_z = accel_z[denbora_arloa_indizeak]

    # Kalkulatu azelerometroaren FFT-a
    N = len(time)
    muestreo_frekuentzia = 1 / (time.iloc[1] - time.iloc[0])
    freq = fftfreq(N, 1 / muestreo_frekuentzia)
    positibo_freq_indizeak = np.where((freq >= 0) & (freq <= args.max_frequency))
    freq = freq[positibo_freq_indizeak]
    fft_x = np.abs(fft(accel_x))[positibo_freq_indizeak]
    fft_y = np.abs(fft(accel_y))[positibo_freq_indizeak]
    fft_z = np.abs(fft(accel_z))[positibo_freq_indizeak]

    # FFT seinalearen luzera inprimatu
    print(f'FFT seinalearen luzera: {len(fft_z)}')

    # Karpeta-muturaren izena eta, behar bada, denbora-tartearen informazioa sartu
    title = f'Medición: {folder_path}'
    if args.start_time is not None and args.end_time is not None:
        title += f'\nDenbora {args.start_time}s-tik {args.end_time}s-raino'

    plt.figure(figsize=(12, 6))
    plt.suptitle(title)

    # Jarraitu kodea aldaketa gabe...
    plt.subplot(2, 1, 1)
    plt.plot(time, accel_x, label='X-ardatza', linewidth=1)
    plt.plot(time, accel_y, label='Y-ardatza', linewidth=1)
    plt.plot(time, accel_z, label='Z-ardatza', linewidth=1)
    plt.xlabel('Denbora')
    plt.ylabel('Azelerazioa [mg]')
    plt.legend()    

    plt.subplot(2, 1, 2)
    plt.plot(freq, fft_z, label='Z-ardatza', linewidth=1)
    plt.xlabel('Frekuentzia [Hz]')
    plt.title('FFT-aren Plot Semilogaritmikoa')
    plt.xlim(0, 5000)

    # Eskatzen den frekuentzia-eremuko indizeak lortu
    freq_indizeak = np.where((freq >= 0) & (freq <= 5000))
    freq = freq[freq_indizeak]
    fft_z = fft_z[freq_indizeak]

    # FFT-aren pikak bilatu eskatzen den aldi batez eta eremu bakoitzean
    # 5 balio baino gehiago dute eskuinean eta ezkerreran
    peak_search_range = int(2 * len(fft_z) / 20)  # Pikuak bilatzeko eremuko luzera definitu

    filtered_peaks = []
    for peak in peaks:
        if (
            peak >= peak_search_range and peak <= len(fft_z) - peak_search_range - 1 and
            all(fft_z[peak] > fft_z[peak - i] for i in range(1, peak_search_range + 1)) and
            all(fft_z[peak] > fft_z[peak + i] for i in range(1, peak_search_range + 1))
        ):
            filtered_peaks.append(peak)

    # Filtratutako piketarako dagoeneko eskatzen den frekuentzia
    peak_frequencies = freq[filtered_peaks]

    # Plot-ean piketarako frekuentziak adierazi
    for freq in peak_frequencies:
        plt.annotate(f'{freq:.2f} Hz', (freq, fft_z[peaks][0]), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.legend()
    plt.tight_layout()

    # Eskatzen den frekuentzia-eremuko indizeak lortu
    freq_indizeak = np.where((freq >= 0) & (freq <= args.max_frequency))
    freq = freq[freq_indizeak]
    fft_z = fft_z[freq_indizeak]

    # Eskatzen den balioa duten pikak lortu
    peaks, _ = find_peaks(fft_z, height=args.max_value if args.max_value is not None else None)

    # Pikak lortu eta zenbaki-tartea adierazi
    print(f'Pikak: {freq[peaks]}')

    # Jatorrizko karpeta-muturaren bidean irudia gordetzeko
    irudia_bidea = os.path.join(folder_path, f'4_bibrazioa_eta_fft_irudia_gorde_{folder_name}_{args.start_time}s_a_{args.end_time}s.png')

    # Irudia gordetzeko
    plt.savefig(irudia_bidea)

    # Irudia gordetako karpeta-muturaren bidean irudia
    irudia_bidea_karpeta = os.path.join(output_folder, f'{folder_name}_{args.start_time}s_a_{args.end_time}s_4_programa.png')

    # Irudia gordetako karpeta-muturaren bidean kopiatu
    shutil.copy(irudia_bidea, irudia_bidea_karpeta)

    # Plot-a erakutsi (aukeran)
    # plt.show()
