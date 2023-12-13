import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import csd, find_peaks
from scipy.fft import fft
import time

# Magnitude Squared Coherence (MSC) kalkulatzeko eta CSV fitxategian gordeko duen funtzioa
def calculate_and_save_msc(folder1, folder2, calculation_number, start_time1=None, end_time1=None, start_time2=None, end_time2=None):
    # Kalkulazioa hasteko denbora gordetzen da
    start_calculation_time = time.time()

    # CSV fitxategiak kargatu
    df1 = pd.read_csv(os.path.join(folder1, 'IIS3DWB_ACC.csv'), delimiter=',')
    df2 = pd.read_csv(os.path.join(folder2, 'IIS3DWB_ACC.csv'), delimiter=',')

    # Azelerazio Z seinaleak atera
    signal1 = df1['A_z [mg]'].to_numpy()
    signal2 = df2['A_z [mg]'].to_numpy()

    time1 = df1['Time']
    time2 = df2['Time']

    # Seinaleak emandako denbora-tartetan moztu
    if start_time1 is not None and end_time1 is not None:
        start_idx1 = np.argmax(time1.values >= start_time1)
        end_idx1 = np.argmax(time1.values >= end_time1)
        signal1 = signal1[start_idx1:end_idx1]

    if start_time2 is not None and end_time2 is not None:
        start_idx2 = np.argmax(time2.values >= start_time2)
        end_idx2 = np.argmax(time2.values >= end_time2)
        signal2 = signal2[start_idx2:end_idx2]

    # Segurtatu bi seinaleek luzera bera duteela
    min_length = min(len(signal1), len(signal2))
    signal1 = signal1[:min_length]
    signal2 = signal2[:min_length]

    # MSC kalkulatu
    fs = 1 / (time1[1] - time1[0])
    freqs, coherence = csd(signal1, signal2, fs=fs, nperseg=min_length, return_onesided=False)
    msc = np.abs(coherence) ** 2

    # Karpeta izenekin eta kalkulazio zenbakiarekin izenburua sortu
    folder1_name = os.path.basename(folder1)
    folder2_name = os.path.basename(folder2)
    
    # Izenburuan hasiera- eta amaiera-denboren orduak gehitu
    title = f'Kalkulazioa #{calculation_number}: Magnitude Squared Coherence {folder1_name} ({start_time1}-{end_time1} s) eta {folder2_name} ({start_time2}-{end_time2} s) artean'

    # MSCn agertzen diren pikak bilatu
    peaks, _ = find_peaks(msc)

    # 5 balio baino handiagoak diren eta 5 baino txikiagoak diren pikak hautatu
    peak_search_range = 5  # Hautatzeko piko bilaketaren tarteko luzera

    filtered_peaks = []
    for peak in peaks:
        if (
            peak >= peak_search_range and peak <= len(msc) - peak_search_range - 1 and
            all(msc[peak] > msc[peak - i] for i in range(1, peak_search_range + 1)) and
            all(msc[peak] > msc[peak + i] for i in range(1, peak_search_range + 1))
        ):
            filtered_peaks.append(peak)

    # Hautatutako pikoei dagozkien frekuentziak lortu
    peak_frequencies = freqs[filtered_peaks]

    # MSC irudirako figura bat sortu
    plt.figure(figsize=(10, 6))
    plt.semilogy(abs(freqs), msc)
    plt.title(title)
    plt.xlabel('Frekuentzia (Hz)')
    plt.ylabel('Magnitude Squared Coherence')
    plt.grid(True)
    plt.xlim(0, 20)

    # Pikoen frekuentziak irudian adierazi
    for freq in peak_frequencies:
        plt.annotate(f'{freq:.2f} Hz', (freq, msc[filtered_peaks][list(peak_frequencies).index(freq)]), textcoords="offset points", xytext=(0, 10), ha='center')

    # Datuen luzera eta kalkulazioaren denbora irudiaren izenean gorde
    elapsed_time = time.time() - start_calculation_time
    print(f'Kalkulazioa #{calculation_number} - {folder1_name} eta {folder2_name} datuen luzera:')
    print(f'Une-seinaleak: {min_length} puntuk')
    print(f'MSC: {len(msc)} puntuk')
    print(f'Kalkulazio denbora: {elapsed_time:.2f} segundo')


    # Irudia gorde hasiera- eta amaiera-denborak izeneko fitxategian
    image_filename = f'{folder1_name}_{folder2_name}_{start_time1}_{end_time1}_{start_time2}_{end_time2}_2_lineal_2_fft.png'
    plt.savefig(image_filename)

# Parseatu lerro deituriko argumentuak
parser = argparse.ArgumentParser(description='Azelerometroen datuak prozesatu eta Magnitude Squared Coherence (MSC) kalkulatu.')
parser.add_argument('folder_paths', type=str, nargs='+', help='Seinaleen CSV fitxategiak gordetzeko karpeta-mutilen bideak')
parser.add_argument('--start_time1', type=float, help='Hasiera denbora, lehenengo karpeta-signalak moztu aurretik')
parser.add_argument('--end_time1', type=float, help='Amaiera denbora, lehenengo karpeta-signalak moztu aurretik')
parser.add_argument('--start_time2', type=float, help='Hasiera denbora, bigarren karpeta-signalak moztu aurretik')
parser.add_argument('--end_time2', type=float, help='Amaiera denbora, bigarren karpeta-signalak moztu aurretik')
args = parser.parse_args()

def main():
    # Karpeta-mutilen bide guztiak sortu eta MSC kalkulatu
    folders = args.folder_paths
    calculation_number = 0
    for i in range(len(folders)):
        for j in range(i + 1, len(folders)):
            calculation_number += 1
            calculate_and_save_msc(folders[i], folders[j], calculation_number, args.start_time1, args.end_time1, args.start_time2, args.end_time2)

if __name__ == "__main__":
    main()
