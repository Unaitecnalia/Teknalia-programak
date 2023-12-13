import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

def calculate_fft(data, fs):
    n = len(data)
    fft_result = np.fft.fft(data)
    freq = np.fft.fftfreq(n, d=1/fs)
    return freq[:n//2], np.abs(fft_result[:n//2])

def find_peaks_custom(fft_data, side_distance=500):
    max_value = np.max(fft_data)
    threshold = max_value / 2

    # fft_data-ren gainetik dagoen lekuan eta gailurra den tokian indices aurkitu
    peaks = []
    for i in range(side_distance, len(fft_data) - side_distance):
        if fft_data[i] > threshold and \
           all(fft_data[i] > fft_data[i-j] for j in range(1, side_distance + 1)) and \
           all(fft_data[i] > fft_data[i+j] for j in range(1, side_distance + 1)):
            peaks.append(i)

    return np.array(peaks)

def plot_fft_comparison(ax, fft_freq, fft1, fft2, label1, label2, freq_limit=2500):
    min_len = min(len(fft_freq), len(fft1), len(fft2))
    freq_limit_idx = np.argmax(fft_freq > freq_limit)

    # FFT1 eta FFT2 arteko konparaketa erakutsi 2500 Hz artean
    ax.plot(fft_freq[:freq_limit_idx], fft1[:freq_limit_idx], label=label1)
    ax.plot(fft_freq[:freq_limit_idx], fft2[:freq_limit_idx], label=label2)

    # FFT1-rako gailurak aurkitu, side_distance=500 erabiliz
    peaks1 = find_peaks_custom(fft1, side_distance=500)
    peaks2 = find_peaks_custom(fft2, side_distance=500)

    # FFT1-rako gailurak erakusteko anotazioak
    for peak in peaks1:
        ax.annotate(f'{fft_freq[peak]:.2f} Hz', (fft_freq[peak], fft1[peak]),
                    textcoords="offset points", xytext=(0, 10), ha='center')

    # FFT2-rako gailurak erakusteko anotazioak
    for peak in peaks2:
        ax.annotate(f'{fft_freq[peak]:.2f} Hz', (fft_freq[peak], fft2[peak]),
                    textcoords="offset points", xytext=(0, 10), ha='center')

    ax.set_title(f"FFT Konparaketa - {label1} vs {label2}")
    ax.set_xlabel("Frekuentzia (Hz)")
    ax.set_ylabel("Amplitudua")
    ax.legend()

def plot_fft_difference(ax, fft_freq, fft1, fft2):
    min_len = min(len(fft_freq), len(fft1), len(fft2))
    fft_diff = np.abs(fft1[:min_len] - fft2[:min_len])
    ax.plot(fft_freq[:min_len], fft_diff)
    ax.set_title("FFT-en Diferentzia Absolutua")
    ax.set_xlabel("Frekuentzia (Hz)")
    ax.set_ylabel("Amplituduen Absolutu Diferentzia")

def plot_fft_no_limit(ax, fft_freq, fft1, fft2, peaks1, peaks2):
    min_len = min(len(fft_freq), len(fft1), len(fft2))
    ax.plot(fft_freq[:min_len], fft1[:min_len], label='FFT1')
    ax.plot(fft_freq[:min_len], fft2[:min_len], label='FFT2')

    # FFT1-rako pikoak erakusteko anotazioak
    for peak in peaks1:
        ax.annotate(f'{fft_freq[peak]:.2f} Hz', (fft_freq[peak], fft1[peak]),
                    textcoords="offset points", xytext=(0, 10), ha='center')

    # FFT2-rako pikoak erakusteko anotazioak
    for peak in peaks2:
        ax.annotate(f'{fft_freq[peak]:.2f} Hz', (fft_freq[peak], fft2[peak]),
                    textcoords="offset points", xytext=(0, 10), ha='center')

    ax.set_title("FFT X-ardatzeko Mugagabea eta piko gabe")
    ax.set_xlabel("Frekuentzia (Hz)")
    ax.set_ylabel("Amplitudua")
    ax.legend()

def save_comparison_plots(folder1, folder2, fft_freq, fft1, fft2):
    # 'konparazioa' izeneko direktorioa sortu, ez bada existitzen
    save_dir = 'konparazioa'
    os.makedirs(save_dir, exist_ok=True)

    # Karpeta izenetan oinarritutako izena sortu
    filename = f'{os.path.basename(folder1)}_{os.path.basename(folder2)}.png'
    save_path = os.path.join(save_dir, filename)

    # Konparaketa erakusteko irudia sortu eta gorde
    fig, axs = plt.subplots(3, 1, figsize=(10, 15))

    # Irudi 1: FFT Konparaketa 2500 Hz artean
    plot_fft_comparison(axs[0], fft_freq, fft1, fft2, label1=os.path.basename(folder1), label2=os.path.basename(folder2), freq_limit=2500)

    # Irudi 2: FFT-en Diferentzia Absolutua
    plot_fft_difference(axs[1], fft_freq, fft1, fft2)

    # FFT1-rako gailurak erakusteko anotazioak, side_distance=500 erabiliz
    peaks1 = find_peaks_custom(fft1, side_distance=500)
    peaks2 = find_peaks_custom(fft2, side_distance=500)

    # Irudi 3: FFT X-ardatzeko Mugagabea eta Gailurak Gabe
    plot_fft_no_limit(axs[2], fft_freq, fft1, fft2, peaks1, peaks2)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="FFT and Plotting")
    parser.add_argument("folders", nargs='+', help="Folder names")
    args = parser.parse_args()

    # Karpeta bakoitzaren pareen kombinazioak sortu
    folder_combinations = list(combinations(args.folders, 2))

    for folder1, folder2 in folder_combinations:
        data1 = pd.read_csv(os.path.join(folder1, "IIS3DWB_ACC.csv"))
        data2 = pd.read_csv(os.path.join(folder2, "IIS3DWB_ACC.csv"))

        # Denbora alea dela suposatuz, fs1 eta fs2 kalkulatu
        fs1 = 1 / (data1["Time"].iloc[1] - data1["Time"].iloc[0])
        fs2 = 1 / (data2["Time"].iloc[1] - data2["Time"].iloc[0])

        fft_freq, fft1 = calculate_fft(data1["A_z [mg]"], fs1)
        _, fft2 = calculate_fft(data2["A_z [mg]"], fs2)

        # fft1[0] eta fft2[0] 0-ra ezarri
        fft1[0] = 0
        fft2[0] = 0

        # Konparaketa irudiak gorde
        save_comparison_plots(folder1, folder2, fft_freq, fft1, fft2)
        
        # Gorde diren fitxategi izena inprimatu
        filename = f'{os.path.basename(folder1)}_{os.path.basename(folder2)}.png'
        print(f'Gordeta: {filename}')

if __name__ == "__main__":
    main()
