import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Obtener la lista de archivos de fibra y galga
archivos_fibra = [f for f in os.listdir() if f.startswith("Fibra")]
archivos_galga = [f for f in os.listdir() if f.startswith("Galga")]

# Ordenar la lista para asegurar el emparejamiento correcto
archivos_fibra.sort()
archivos_galga.sort()

# Crear un directorio para almacenar las imágenes si no existe
directorio_imagenes = "imagenes_6_gráficas"
if not os.path.exists(directorio_imagenes):
    os.makedirs(directorio_imagenes)

# Iterar sobre los archivos de fibra y galga
for i, (archivo_fibra, archivo_galga) in enumerate(zip(archivos_fibra, archivos_galga), start=1):

    # Leer el primer archivo CSV con delimitador de tabulador
    df_ensayo = pd.read_csv(archivo_fibra, delimiter='\t')

    # Leer el segundo archivo CSV con delimitador ; y coma como separador decimal
    df_galgas = pd.read_csv(archivo_galga, delimiter=';', decimal=',')

    # Seleccionar la columna específica para la calibración de ensayo
    columna_ensayo = "Wavelength 1 [nm]"

    # Seleccionar las seis columnas de las galgas para la calibración
    columnas_galgas = ["G1 - CENTRO SUP [?m/m]", "G2 - CENTRO SUP [?m/m]", "G3 - CENTRO INF [?m/m]",
                       "G4 - CENTRO INF [?m/m]", "G5 - LAT SUP [?m/m]", "G6 - LAT INF [?m/m]"]

    # Calcular la media de df_galgas y df_ensayo para todas las columnas
    medias_galgas = df_galgas.mean()


    # Calcular la media de df_ensayo para la columna específica
    media_fibra = df_ensayo[columna_ensayo].mean()
    
    media_primeros_10 = df_ensayo[columna_ensayo].head(10).mean()

    # Seleccionar las 10 filas en la mitad del DataFrame y calcular la media
    num_filas = len(df_ensayo[columna_ensayo])
    media_en_la_mitad = df_ensayo[columna_ensayo].iloc[num_filas // 2 - 5 : num_filas // 2 + 5].mean()

    
    if media_en_la_mitad - media_primeros_10 > 0:
        df_ensayo[columna_ensayo] = -1 * df_ensayo[columna_ensayo]

    # Verificar si el producto de las medias es positivo para cada columna
    for columna_galga in columnas_galgas:
        media_galga = medias_galgas[columna_galga]
        
        if media_galga * media_fibra > 0:
            # Multiplicar la columna específica de df_galgas por -1
            df_galgas[columna_galga] = -1 * df_galgas[columna_galga]
            print(media_galga * media_fibra)
            print("media galga: ", media_galga)
            print("media fibra: ", media_fibra)

    # Crear una nueva figura con 6 subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, columna_galgas in enumerate(columnas_galgas):
    
    
        # Obtener los valores de las columnas
        puntos_galgas = df_galgas[columna_galgas].values
        puntos_ensayo = df_ensayo[columna_ensayo].values
        puntos_ensayo = 3000 - puntos_ensayo

        # Calcular el desplazamiento para maximizar la correlación en valor absoluto
        correlacion = np.correlate(puntos_ensayo, abs(puntos_galgas), mode='full')
        shift = np.argmax(np.abs(correlacion)) - len(df_ensayo) + 1
        print(correlacion)
        print(len(correlacion))
        print(max(correlacion))
        print(shift)
    
        # Graficar la fibra óptica en el primer conjunto de ejes Y (azul)
        ax = axes[i]
        ax.plot(df_ensayo[columna_ensayo].shift(shift), label='ENSAYO PRENSA', color='blue')
        ax.set_xlabel("Índice de Tiempo")
        ax.set_ylabel("Valor Normalizado", color='blue')
        ax.set_title(f"{'ENSAYO PRENSA'} - Galga {i+1}")
        ax.legend()
        ax.grid(True)

        # Crear un nuevo conjunto de ejes Y (rojo) para las galgas
        ax2 = ax.twinx()
        ax2.set_ylabel("Valor Normalizado", color='red')

        # Graficar la columna de las galgas en el segundo conjunto de ejes Y
        ax2.plot(df_galgas[columna_galgas], label=columna_galgas, color='red', alpha=0.7)
        ax2.legend()
        
    # Ajustar diseño
    plt.tight_layout()
    
    plt.show()

    # Guardar la imagen con el nombre deseado
    nombre_fibra = os.path.splitext(archivo_fibra)[0]
    nombre_galga = os.path.splitext(archivo_galga)[0]
    nombre_imagen = f"{directorio_imagenes}/{nombre_fibra}_{nombre_galga}.png"
    plt.savefig(nombre_imagen)

    # Cerrar la figura actual para evitar la superposición en la siguiente iteración
    plt.close()
