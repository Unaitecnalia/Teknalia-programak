import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def main():
    if len(sys.argv) != 4:
        print("Erabilera: python programa.py karpeta_bidea hasiera_segundoak amaiera_segundoak")
        return

    karpeta_bidea = sys.argv[1]
    csv_fitxategia = "IIS3DWB_ACC.csv"  # Egindako fitxategiaren izena
    hasiera_segundoak = float(sys.argv[2])
    amaiera_segundoak = float(sys.argv[3])

    bidea_osorik = os.path.join(karpeta_bidea, csv_fitxategia)

    # CSV fitxategia DataFrame batean kargatu
    try:
        datuak = pd.read_csv(bidea_osorik)
    except FileNotFoundError:
        print(f"Ezin izan da {bidea_osorik} fitxategia aurkitu")
        return

    # Hasierako eta amaierako datuak arteko zatiak hartu
    datuak = datuak[(datuak['Time'] >= hasiera_segundoak) & (datuak['Time'] <= amaiera_segundoak)]

    # Denbora eta A_z osagaik hartu
    denbora = datuak['Time'].values
    az = datuak['A_z [mg]'].values

    # Muestreoaren (fs) balioa kalkulatu
    fs = 1 / (denbora[1] - denbora[0])

    # A_z-ren FFTa kalkulatu
    n = len(az)
    fft_az = np.fft.fft(az)
    freq = np.fft.fftfreq(n, 1 / fs)
    fft_az = fft_az[:n // 2]  # Frequentzia erdi bakarrik hartu
    freq = freq[:n // 2]

    # FFTan pikak bilatu
    pikak, _ = find_peaks(np.abs(fft_az), height=None)  # Thresholdea ez da ezartzen

    # 5 balio ezkerretik eta 5 eskumatik handiagoak diren pikak hautatu
    piken_bilaketa_ariketa = int(2 * len(fft_az) / 15000)  # Pikoak bilatzeko ariketa eremua zehaztu
    print(piken_bilaketa_ariketa)

    hautatutako_pikak = []
    for piko in pikak:
        if (
            piko >= piken_bilaketa_ariketa and piko <= len(fft_az) - piken_bilaketa_ariketa - 1 and
            all(fft_az[piko] > fft_az[piko - i] for i in range(1, piken_bilaketa_ariketa + 1)) and
            all(fft_az[piko] > fft_az[piko + i] for i in range(1, piken_bilaketa_ariketa + 1))
        ):
            hautatutako_pikak.append(piko)

    # Piketan dagoen frekuentzia kalkulatu
    hautatutako_piken_frekuentziak = freq[hautatutako_pikak]

    # Frekuentzia eta FFTaren balioen eremu berdina izan dezaten, bateratu
    max_frekuentzia = 50  # Erakusteko nahi duzun frekuentzia maximoa zehaztu
    frekuentzia_eremuak = freq[freq <= max_frekuentzia]
    fft_eremuak = np.abs(fft_az[:len(frekuentzia_eremuak)])

    # Bi subplot sortu seinaleari eta bere FFTari
    fig, axs = plt.subplots(2, 1, figsize=(8, 6))
    axs[0].plot(denbora, az)
    axs[0].set_title('A_z vs Denbora')
    axs[0].set_xlabel('Denbora (s)')
    axs[0].set_ylabel('A_z [mg]')

    axs[1].semilogy(frekuentzia_eremuak, fft_eremuak)
    axs[1].set_title('A_z-ren FFT vs Frekuentzia')
    axs[1].set_xlabel('Frekuentzia (Hz)')
    axs[1].set_ylabel('Amplitud')
    axs[1].set_xlim(0, max_frekuentzia)  # Eremuaren mugak 0-50 Hz-ra mugatu
    
    # Adierazi pikak grafikoan
    for frekuentzia, piko in zip(hautatutako_piken_frekuentziak, hautatutako_pikak):
        plt.annotate(f'{frekuentzia:.2f} Hz', (frekuentzia, np.abs(fft_az)[piko]), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.tight_layout()
        
    # FFTaren balioak inprimatu
    print("FFTaren balioak:")
    for f, balioa in zip(frekuentzia_eremuak, fft_eremuak):
        print(f"Frekuentzia: {f:.2f} Hz, Amplitud: {balioa:.2f}")

    # Irudia gordetu
    izena_png = f'CSV_moztua_{os.path.basename(karpeta_bidea)}_{int(hasiera_segundoak)}_{int(amaiera_segundoak)}.png'
    plt.savefig(izena_png)

    print(f"Datuak gordeta {izena_png}-n")
    
    # Datuak CSV fitxategi batean gorde
    izena_csv = f'CSV_moztua_{os.path.basename(karpeta_bidea)}_{int(hasiera_segundoak)}_{int(amaiera_segundoak)}.csv'
    datuak_moztua = pd.DataFrame({'Time': denbora, 'A_z [mg]': az})
    datuak_moztua.to_csv(izena_csv, index=False)

    print(f"Datuak gordeta {izena_csv}-n")

if __name__ == "__main__":
    main()
