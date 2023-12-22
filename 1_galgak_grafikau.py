import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Obtener el directorio de trabajo actual
directorio = os.getcwd()

# Crear un subdirectorio "resultados" si no existe
subdirectorio_resultados = os.path.join(directorio, 'resultados')
os.makedirs(subdirectorio_resultados, exist_ok=True)

# Obtener la lista de archivos CSV en el directorio
archivos_csv = [archivo for archivo in os.listdir(directorio) if archivo.endswith('.csv')]

# Procesar cada archivo CSV
for archivo in archivos_csv:
    # Construir la ruta completa al archivo
    ruta_archivo = os.path.join(directorio, archivo)

    try:
        # Cargar datos desde el CSV con punto y coma como delimitador
        data = pd.read_csv(ruta_archivo, delimiter=';', decimal=',')

        # Calcular fs
        time_interval = data['Time  1 - default sample rate [s]'].diff().mean()
        fs = 1 / time_interval

        # Obtener el nombre base del archivo (sin la extensión .csv)
        nombre_base = os.path.splitext(archivo)[0]

        # Graficar cada columna en una figura separada
        for col in data.columns[1:]:  # Excluir la columna 'Time'
            plt.figure(figsize=(10, 4))

            # Graficar la columna
            plt.subplot(2, 1, 1)
            plt.plot(data['Time  1 - default sample rate [s]'], data[col])
            plt.title(f'Gráfico de {col} - {archivo}')
            plt.xlabel('Tiempo (s)')
            plt.ylabel('Amplitud')

            # Realizar FFT de la columna
            plt.subplot(2, 1, 2)
            signal = data[col]
            fft_result = np.fft.fft(signal)
            freq = np.fft.fftfreq(len(signal), d=time_interval)

            # Mostrar solo el 5% de los primeros valores en el eje x
            num_values_to_show = int(0.05 * len(freq))
            plt.semilogy(freq[:num_values_to_show], np.abs(fft_result[:num_values_to_show]))
            
            plt.title(f'FFT de {col} - {archivo}')
            plt.xlabel('Frecuencia (Hz)')
            plt.ylabel('Amplitud FFT')

            plt.tight_layout()  # Ajustar diseño para evitar superposición

            # Modificar el nombre del archivo para eliminar caracteres especiales
            nombre_columna = col[:-6]  # Eliminar los últimos 6 caracteres del nombre de la columna
            nombre_figura = f'{nombre_base}_{nombre_columna}.png'
            
            # Guardar la figura en el subdirectorio "resultados"
            ruta_guardado = os.path.join(subdirectorio_resultados, nombre_figura)
            plt.savefig(ruta_guardado)
            # plt.show()

    except pd.errors.ParserError as e:
        print(f"Error al leer el archivo {archivo}: {e}")
