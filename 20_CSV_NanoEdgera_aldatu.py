import pandas as pd
import os
import time
import sys

def procesar_carpeta(nombre_carpeta):
    # CSV fitxategiaren path-a
    ruta_original = os.path.join(nombre_carpeta, "IIS3DWB_ACC.csv")

    # DataFrame-a kargatu CSV fitxategi originaletatik
    inicio_carga = time.time()
    df = pd.read_csv(ruta_original)
    fin_carga = time.time()

    # fs originala kalkulatu
    tiempo_inicial = df['Time'].iloc[0]
    tiempo_final = df['Time'].iloc[-1]
    cantidad_muestras = len(df)
    fs_original = 1 / ((tiempo_final - tiempo_inicial) / (cantidad_muestras - 1))

    # fs-n jartzeko eskalatze faktorea kalkulatu
    fs_nuevo = fs_original
    factor_escala = int(round(fs_original / fs_nuevo))

    print(f'Original muestreo-frekuentzia (fs_original): {fs_original:.4f} Hz')
    print(f'fs_original / fs_irteera ratio: {factor_escala}')

    # fs_original / fs_nuevo bakoitzean lerro bat hartu
    df_subset = df.iloc[::factor_escala]

    # Time zutabea kendu
    df_subset = df_subset.drop(columns=['Time'])

    # Lerroak gordetzeko zerrenda hasieratu
    df_list = [[]]
    fila_actual = []  # Lerro bakoitzeko zerrenda berri bat sortu

    inicio_calculo = time.time()

    # df_subset lerroetan iteratu eta zerrendan gehitu
    for i in range(len(df_subset)):
        # df_subset zutabeetan iteratu
        for j in range(0, len(df_subset.columns), 3):
            # Uneko zutabeak hartu eta lerro bakoitzeko zerrendan gehitu
            columnas_actuales = df_subset.iloc[i, j:j+3].values.flatten()
            fila_actual.extend(columnas_actuales)
        # Egiaztatu lerro aktualeak zutabe kopurua zehatz 768 dela
        if len(fila_actual) == 768:
            # Gehitu lerro aktuala zerrendan
            df_list.append(fila_actual)
            fila_actual = []  # Lerro bakoitzeko zerrenda berri bat sortu

    # Zerrendatik DataFrame bat sortu
    df_replicado = pd.DataFrame(df_list)

    fin_calculo = time.time()

    inicio_guardado = time.time()

    df_replicado = df_replicado.drop(df.index[0])

    df_replicado.reset_index(drop=True, inplace=True)

    # DataFrame berria CSV fitxategi batean gorde
    nombre_nuevo_csv = f'NanoEdgeCSV_{nombre_carpeta}.csv'
    df_replicado.to_csv(nombre_nuevo_csv, index=False)

    # CSV fitxategia irakurri eta lehenengo lerroa baztertu
    df_nuevo = pd.read_csv(nombre_nuevo_csv, skiprows=1)

    # DataFrame-a lehenengo lerroa gabe CSV fitxategian gorde
    df_nuevo.to_csv(nombre_nuevo_csv, index=False)
    print("DataFrame dimensions: ", df_replicado.shape)
    print("\nGordeta: ", nombre_nuevo_csv)
    print()

    fin_guardado = time.time()

    # Inprimatu fitxategi originalaren eta helburuko fitxategiaren errenkaden kopurua
    filas_originales = len(df) - 1  # Zutabeen izenak baztertzen
    filas_destino = len(df_replicado)
    print(f'Zutabe originalen kopurua: {filas_originales}')
    print(f'Helburuko fitxategiko lerro kopurua: {filas_destino}')

    # Errenkaden arteko banaketa kalkulatu eta inprimatu
    division_filas = filas_originales / filas_destino
    print(f'Zutabe originalen eta helburuko fitxategiko arteko banaketa: {division_filas:.4f}')

    # Denborak inprimatu
    tiempo_carga = fin_carga - inicio_carga
    tiempo_guardado = fin_guardado - inicio_guardado
    tiempo_calculo = fin_calculo - inicio_calculo

    print(f'Kargatze denbora: {tiempo_carga:.4f} segundo')
    print(f'Gordetze denbora: {tiempo_guardado:.4f} segundo')
    print(f'Kalkulatze denbora: {tiempo_calculo:.4f} segundo')
    print(f'Guztira denbora: {tiempo_carga + tiempo_guardado + tiempo_calculo:.4f} segundo')

if __name__ == "__main__":
    # Komando lerroan argumentu bakarra ematen dela egiaztatu
    if len(sys.argv) != 2:
        print("Mesedez, eman karpeta izena argumentu gisa.")
        sys.exit(1)

    # Komando lerroko argumentuetatik karpeta izena lortu
    nombre_carpeta = sys.argv[1]

    # Karpeta prozesatu
    procesar_carpeta(nombre_carpeta)
