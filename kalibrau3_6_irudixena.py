import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Obtener la lista de archivos de fibra y galga
archivos_fibra = [f for f in os.listdir() if f.startswith("Fibra")]# and f.endswith("_50KN_TEST2_ensayo.csv")]
archivos_galga = [f for f in os.listdir() if f.startswith("Galga")]# and f.endswith("_TEST2_galgas.csv")]

# Ordenar la lista para asegurar el emparejamiento correcto
archivos_fibra.sort()
archivos_galga.sort()

# Iterar sobre los archivos de fibra y galga
for i, (archivo_fibra, archivo_galga) in enumerate(zip(archivos_fibra, archivos_galga), start=1):

    # Leer el primer archivo CSV con delimitador de tabulador
    archivo_fibra = "Fibra2_50KN_TEST2_ensayo.csv"
    df_ensayo = pd.read_csv(archivo_fibra, delimiter='\t')

    # Leer el segundo archivo CSV con delimitador ; y coma como separador decimal
    archivo_galga = "Galga2_TEST2_galgas.csv"
    df_galgas = pd.read_csv(archivo_galga, delimiter=';', decimal=',')

    # Seleccionar la columna específica para la calibración de ensayo
    columna_ensayo = "Wavelength 1 [nm]"

    # Seleccionar las seis columnas de las galgas para la calibración
    columnas_galgas = ["G1 - CENTRO SUP [?m/m]", "G2 - CENTRO SUP [?m/m]", "G3 - CENTRO INF [?m/m]",
                       "G4 - CENTRO INF [?m/m]", "G5 - LAT SUP [?m/m]", "G6 - LAT INF [?m/m]"]

    # Cambiar el nombre del label para Fibra Óptica
    label_ensayo = "Fibra Óptica"


    # Calcular la media de df_galgas
    media_galgas = df_galgas.mean().mean()

    # Normalizar los puntos del ensayo en función del signo de la media de df_galgas
    if media_galgas > 0:
        # Opción 1
        min_ensayo = df_ensayo[columna_ensayo].max()
        df_ensayo[columna_ensayo] = df_ensayo[columna_ensayo] - min_ensayo

        max_galgas = min(df_galgas[columna].min() for columna in columnas_galgas)
        max_ensayo = df_ensayo[columna_ensayo].min()
    else:
        # Opción 2
        min_ensayo = df_ensayo[columna_ensayo].min()
        df_ensayo[columna_ensayo] = df_ensayo[columna_ensayo] - min_ensayo

        max_galgas = max(df_galgas[columna].max() for columna in columnas_galgas)
        max_ensayo = df_ensayo[columna_ensayo].max()

    # Realizar el ajuste del desplazamiento para maximizar la correlación
    max_correlation = 0
    best_shift = 0

    for i, columna_galgas in enumerate(columnas_galgas):
        puntos_galgas = df_galgas[columna_galgas] * (max_ensayo / max_galgas)

        # Calcular la correlación entre el ensayo y la galga actual
        correlation = np.correlate(df_ensayo[columna_ensayo], puntos_galgas, mode='full')
        shift = np.argmax(correlation) - len(df_ensayo) + 1

        if abs(correlation[shift]) > abs(max_correlation):
            max_correlation = correlation[shift]
            best_shift = shift
            print(max_correlation," ",best_shift)
            
    # Imprimir el desplazamiento calculado por pantalla
    print(f"Desplazamiento calculado: {best_shift} puntos")

    # Guardar el mejor desplazamiento en un archivo
    archivo_desplazamiento = "mejor_desplazamiento.txt"
    with open(archivo_desplazamiento, "w") as file:
        file.write(str(best_shift))

    # Aplicar el mejor desplazamiento a los datos del ensayo
    df_ensayo[columna_ensayo] = df_ensayo[columna_ensayo].shift(100, fill_value=0)
    # Crear una nueva figura con 6 subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    print(df_galgas)
    # Graficar la fibra óptica en todos los subplots
    for i, ax in enumerate(axes):
        ax.plot(df_ensayo[columna_ensayo], label=label_ensayo, color='blue')
        ax.set_xlabel("Índice de Tiempo")
        ax.set_ylabel("Valor Normalizado")
        ax.set_title(f"{label_ensayo} - Galga {i+1}")
        ax.legend()
        ax.grid(True)
    print(max_ensayo)
    print(max_galgas)
    # Graficar encima de cada subplot una columna de las galgas con puntos normalizados
    for i, columna_galgas in enumerate(columnas_galgas):
        ax = axes[i]
        puntos_galgas = df_galgas[columna_galgas] * (max_ensayo / max_galgas)
        ax.plot(puntos_galgas, label=columna_galgas, color='red', alpha=0.7)
        ax.legend()

    # Ajustar diseño
    plt.tight_layout()
    plt.show()
