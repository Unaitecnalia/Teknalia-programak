import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Fibra eta galga fitxategien zerrenda lortu
archivos_fibra = [f for f in os.listdir() if f.startswith("Fibra")]
archivos_galga = [f for f in os.listdir() if f.startswith("Galga")]

# Zerrenda ordenatu emparejatze zuzena bermatzeko
archivos_fibra.sort()
archivos_galga.sort()

# Irudiak gordetzeko direktorioa sortu ez bada, sortu
directorio_imagenes = "imagenes_6_gráficas"
if not os.path.exists(directorio_imagenes):
    os.makedirs(directorio_imagenes)

# Fibra eta galga fitxategiak iteratu
for i, (archivo_fibra, archivo_galga) in enumerate(zip(archivos_fibra, archivos_galga), start=1):

    # Lehenengo CSV fitxategia irakurri tabulatzailearen arabera
    df_ensayo = pd.read_csv(archivo_fibra, delimiter='\t')

    # Bigarren CSV fitxategia irakurri ';' eta komaren arabera
    df_galgas = pd.read_csv(archivo_galga, delimiter=';', decimal=',')

    # Etiketa bakoitzeko zutabak hautatu kalibratzeko
    columna_ensayo = "Wavelength 1 [nm]"

    # Kalibratzeko galguen sei zutabe hautatu
    columnas_galgas = ["G1 - CENTRO SUP [?m/m]", "G2 - CENTRO SUP [?m/m]", "G3 - CENTRO INF [?m/m]",
                       "G4 - CENTRO INF [?m/m]", "G5 - LAT SUP [?m/m]", "G6 - LAT INF [?m/m]"]

    # df_galgas eta df_ensayo bakoitzean media kalkulatu
    medias_galgas = df_galgas.mean()

    # df_ensayo-ko media kalkulatu espezifikoko zutabetarako
    media_fibra = df_ensayo[columna_ensayo].mean()
    
    # df_ensayo-ren lehenengo 10 balioen media kalkulatu
    media_primeros_10 = df_ensayo[columna_ensayo].head(10).mean()

    # DataFramaren erdiaren 10 errenkada hartu eta media kalkulatu
    num_filas = len(df_ensayo[columna_ensayo])
    media_en_la_mitad = df_ensayo[columna_ensayo].iloc[num_filas // 2 - 5 : num_filas // 2 + 5].mean()

    # Baldin eta media_en_la_mitad - media_primeros_10 > 0 bada
    if media_en_la_mitad - media_primeros_10 > 0:
        df_ensayo[columna_ensayo] = -1 * df_ensayo[columna_ensayo]

    # Media guztietako produktua positiboa den ala ez ikusi
    for columna_galga in columnas_galgas:
        media_galga = medias_galgas[columna_galga]
        
        if media_galga * media_fibra > 0:
            # df_galgas-ko zutabe espezifikoa -1 biderkatu
            df_galgas[columna_galga] = -1 * df_galgas[columna_galga]
            print(media_galga * media_fibra)
            print("media galga: ", media_galga)
            print("media fibra: ", media_fibra)

    # 6 subplot dituen figura berri bat sortu
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, columna_galgas in enumerate(columnas_galgas):
    
        # Zutabeen balioak hartu
        puntos_galgas = df_galgas[columna_galgas].values
        puntos_ensayo = df_ensayo[columna_ensayo].values
        puntos_ensayo = 3000 - puntos_ensayo

        # Korrelazioa maximizatzeko desplazamendua kalkulatu
        correlacion = np.correlate(puntos_ensayo, abs(puntos_galgas), mode='full')
        shift = np.argmax(np.abs(correlacion)) - len(df_ensayo) + 1
        print(correlacion)
        print(len(correlacion))
        print(max(correlacion))
        print(shift)
    
        # 'ENSAYO PRENSA' lehenengo Y-ko (urdina) ariketak
        ax = axes[i]
        ax.plot(df_ensayo[columna_ensayo].shift(shift), label='ENSAYO PRENSA', color='blue')
        ax.set_xlabel("Denbora (s)")
        ax.set_ylabel("Argiaren uhin luzera [nm]", color='blue')
        ax.set_title(f"{'PRENTSA SAIOA'} - Galga {i+1}")
        ax.legend()
        ax.grid(True)

        # 'ENSAYO PRENSA' lehenengo Y-ko (gorria) ariketak sortu
        ax2 = ax.twinx()
        ax2.set_ylabel("Galgaren microstrains", color='red')

        # Galguen zutabea bigarren Y-ko (gorria) ariketetan marraztu
        ax2.plot(df_galgas[columna_galgas], label=columna_galgas, color='red', alpha=0.7)
        ax2.legend()
        
    # Diseinua egokitu
    plt.tight_layout()
    
    # plt.show()

    # Irudia gordetzeko izena ezarri
    directorio_imagenes = "imagenes_6_gráficas"
    if not os.path.exists(directorio_imagenes):
        os.makedirs(directorio_imagenes)

    directorio_imagenes = os.path.abspath("imagenes_6_gráficas")

    nombre_imagen = f"{directorio_imagenes}/{archivo_fibra}_{archivo_galga}.png"
    print(f"Guardando imagen en: {nombre_imagen}")
    plt.savefig(nombre_imagen)

    # Gaurkotasuna ekiditzeko uneko figuraren itxiera
    plt.close()
