import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import csd, find_peaks
from scipy.fft import fft
import time
from itertools import combinations

# Magnitude Squared Coherence (MSC) kalkulatzeko eta CSV fitxategian gordetzeko funtzioa
def calculate_and_save_msc(folder1, folder2, calculation_number, start_time):
    
    # CSV fitxategiak kargatu
    df1 = pd.read_csv(os.path.join(folder1, 'IIS3DWB_ACC.csv'), delimiter=',')
    df2 = pd.read_csv(os.path.join(folder2, 'IIS3DWB_ACC.csv'), delimiter=',')

    # Azelerazio Z seinaleak atera
    signal1 = df1['A_z [mg]'].to_numpy()
    signal2 = df2['A_z [mg]'].to_numpy()

    time1 = df1['Time']
    time2 = df2['Time']

    
    # Bi seinaleen luzera txikiena hartu
    min_length = min(len(signal1), len(signal2))

    # Bi seinaleek luzera berdina izan dezaten ziurtatu
    signal1 = signal1[:min_length]
    signal2 = signal2[:min_length]
    time1 = time1[:min_length]
    time2 = time2[:min_length]

    # Frekuentzia muestreoa (fs) kalkulatu
    fs = (len(df1) - 1) / (df1.iloc[-1, 0] - df1.iloc[0, 0])

    # Seinaleen FFT kalkulatu
    fft_signal1 = fft(signal1)
    fft_signal2 = fft(signal2)
    freq_fft = np.fft.fftfreq(min_length, 1 / fs)

    # FFT-ak 0 Hz-tik eta 15 Hz-tik gora diren balioak 0 izateko
    fft_filtered_signal1 = fft_signal1.copy()
    fft_filtered_signal2 = fft_signal2.copy()
    freq_fft_filtered = np.fft.fftfreq(min_length, 1 / fs)

    # 0 Hz eta 15 Hz-tik gora diren balioak 0 izatera ezarri
    freq_cutoff_low = 0.1  # Kortxoa beherako frekuentzia
    freq_cutoff_high = 15.0  # Kortxoa goraeko frekuentzia
    fft_filtered_signal1[(freq_fft < freq_cutoff_low) | (freq_fft > freq_cutoff_high)] = 0
    fft_filtered_signal2[(freq_fft < freq_cutoff_low) | (freq_fft > freq_cutoff_high)] = 0

    # FFT-aren inbertituak hartu, seinaleak lortu
    filtered_signal1 = np.real(np.fft.ifft(fft_filtered_signal1))
    filtered_signal2 = np.real(np.fft.ifft(fft_filtered_signal2))

    freq_fft = np.fft.fftfreq(min_length, 1 / fs)

    # MSC kalkulatu
    freqs, coherence = csd(filtered_signal1, filtered_signal2, fs=fs, nperseg=min_length, return_onesided=False)
    msc = np.abs(coherence) ** 2

    # Karpeta izenekin titulua sortu
    folder1_name = os.path.basename(folder1)
    folder2_name = os.path.basename(folder2)
    title = f'Magnitude Squared Coherence {folder1_name} eta {folder2_name} artean'

    # MSCn dauden pikak aurkitu
    peaks, _ = find_peaks(msc)

    # 5 balio baino ez diren inguruko pikoak aurkitu
    peak_search_range = 1  # Pikoak bilatzeko tartea definitu

    filtered_peaks = []
    for peak in peaks:
        if (
            peak >= peak_search_range and peak <= len(msc) - peak_search_range - 1 and
            all(msc[peak] > msc[peak - i] for i in range(1, peak_search_range + 1)) and
            all(msc[peak] > msc[peak + i] for i in range(1, peak_search_range + 1))
        ):
            filtered_peaks.append(peak)

    # Pikoei dagozkien frekuentziak lortu
    peak_frequencies = freqs[filtered_peaks]

    plt.figure(figsize=(10, 6))
    
    plt.suptitle(f'MSC {folder1_name} eta {folder2_name} artean', fontsize=16)

    # Grafika batzuk sortu
    plt.subplot(3, 1, 3)  # Hiru lerro, zutabe bat, hirugarren subplota
    plt.plot(abs(freqs), msc)
    plt.title(title)
    plt.xlabel('Frekuentzia (Hz)')
    plt.ylabel('Magnitude Squared Coherence')
    plt.xlim(0, 20)  # Frekuentzia-eremuan mugatu
    plt.grid(True)

    # Grafika batzuk sortu
    plt.subplot(3, 2, 1)  # Hiru lerro, bi zutabe, lehen subplota
    plt.plot(time1, filtered_signal1)
    plt.title('Filtratutako Seinale 1')
    plt.xlabel('Denbora')
    plt.ylabel('Amplitud')
    plt.grid(True)

    plt.subplot(3, 2, 2)  # Hiru lerro, bi zutabe, bigarren subplota
    plt.plot(time2, filtered_signal2)
    plt.title('Filtratutako Seinale 2')
    plt.xlabel('Denbora')
    plt.ylabel('Amplitud')
    plt.grid(True)

    # Grafika batzuk sortu
    plt.subplot(3, 2, 3)  # Hiru lerro, bi zutabe, hirugarren subplota
    plt.semilogy(freq_fft[:min_length // 2], np.abs(fft_filtered_signal1[:min_length // 2]), label='FFT Filtratua 1')
    plt.title('FFT Filtratua Seinale 1')
    plt.xlabel('Frekuentzia (Hz)')
    plt.ylabel('Amplitud')
    plt.xlim(0, 20)  # Frekuentzia-eremuan mugatu
    plt.grid(True)

    plt.subplot(3, 2, 4)  # Hiru lerro, bi zutabe, laugarren subplota
    plt.semilogy(freq_fft[:min_length // 2], np.abs(fft_filtered_signal2[:min_length // 2]), label='FFT Filtratua 2')
    plt.title('FFT Filtratua Seinale 2')
    plt.xlabel('Frekuentzia (Hz)')
    plt.ylabel('Amplitud')
    plt.xlim(0, 20)  # Frekuentzia-eremuan mugatu
    plt.grid(True)

    # Pikoei dagozkien frekuentziak grafikoan adierazi
    for freq in peak_frequencies:
        plt.annotate(f'{freq:.2f} Hz', (freq, msc[filtered_peaks][list(peak_frequencies).index(freq)]), textcoords="offset points", xytext=(0, 10), ha='center')

    # Kalkulua zenbatgarria izan daitekeen ikusi
    print(f'Kalkulua #{calculation_number} - {folder1_name} eta {folder2_name} datuen luzera:')
    print(f'Denbora-seinaleak: {min_length} puntuk')
    print(f'MSC: {len(msc)} puntuk')
    print(f'Seinaleen FFTa denbora-seinaleetan: {len(fft_signal1)} puntuk')

    # Balioak freq, msc, filtered_signal1 eta filtered_signal2 fitxategi CSV batean gorde
    data = pd.DataFrame({
        'freq': freqs,
        'MSC': msc,
        'Filtered_Signal1': filtered_signal1,
        'Filtered_Signal2': filtered_signal2,
        'FFT_Signal1': fft_signal1,
        'FFT_Signal2': fft_signal2,
        'FFT_Filtered_Signal1': fft_filtered_signal1,
        'FFT_Filtered_Signal2': fft_filtered_signal2,
        'signal1': signal1,
        'signal2': signal2,
    })
    
    # Irudia gorde
    image_filename = f'{folder1_name}_{folder2_name}_2_line
