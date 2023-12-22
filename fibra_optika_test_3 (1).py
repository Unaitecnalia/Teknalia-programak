import os
import pandas as pd
import numpy as np
from scipy.fft import fft
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Directorio que contiene los archivos sin extensión o con extensión .xlsx
directorio = 'Pruebak'

# Enumerar los archivos en el directorio que terminan en .xlsx
archivos = [archivo for archivo in os.listdir(directorio) if archivo.endswith(".xlsx") or not "." in archivo]

print(f'{archivos}')

# Iterar a través de los archivos
for archivo in archivos:
    if not "." in archivo:

        # Construye la ruta completa del archivo
        ruta_completa = os.path.join(directorio, archivo)

        # Cargar el archivo (maneja .xlsx si es necesario)
        if archivo.endswith(".xlsx"):
            df = pd.read_excel(ruta_completa)
        else:
            df = pd.read_csv(ruta_completa, delimiter='\t')

        # Seleccionar todas las filas y las columnas de píxeles (desde la cuarta columna hasta el final)
        pixels = df.iloc[:, 3:]

        # Convertir los valores de píxeles a un arreglo NumPy
        pixel_values = pixels.to_numpy()

        # Elimina el último valor del array si es NaN
        if np.isnan(pixel_values[-1, -1]):
            pixel_values = pixel_values[:, :-1]

        # # Encontrar los picos en la MSC que cumplen con los criterios
        # peaks, _ = find_peaks(np.abs(pixel_values[0]))  # Asumiendo que deseas encontrar picos en la primera fila de la FFT

        # # Filtrar los picos que son mayores que 5 valores a su izquierda y 5 a la derecha
        # peak_search_range = 50  # Define la longitud del rango de búsqueda de picos

        # filtered_peaks = []
        # for peak in peaks:
            # if (
                # peak >= peak_search_range and peak <= len(pixel_values[0]) - peak_search_range - 1 and
                # all(pixel_values[0, peak] > pixel_values[0, peak - i] for i in range(1, peak_search_range + 1)) and
                # all(pixel_values[0, peak] > pixel_values[0, peak + i] for i in range(1, peak_search_range + 1))
            # ):
                # filtered_peaks.append(peak)

        # Identificar las columnas que comienzan con "Wavelength"
        columnas_wavelength = [col for col in df.columns if col.startswith("Wavelength")]

        print(f' {archivo}: {len(columnas_wavelength)}')

        if len(columnas_wavelength) > 0:
            # Parse and convert the "Time" column to datetime format
            df['Time'] = pd.to_datetime(df['Time'], format='%I:%M:%S %p', errors='coerce')

            # Iterate through the "Wavelength" columns and create subplots
            for i, column_name in enumerate(columnas_wavelength):
                # Create a new figure with two subplots
                fig, axs = plt.subplots(2, 1, figsize=(12, 12))

                # Plot 1: Original signal
                axs[0].set_title(f'Original Signal - "Wavelength" {i + 1} in the file {archivo}')
                axs[0].plot(df['Time'], df[column_name])
                axs[0].set_xlabel('Time')
                axs[0].set_ylabel('Amplitude')
                axs[0].grid()
                axs[0].get_yaxis().get_major_formatter().set_useOffset(False)

                # Plot 2: FFT of the signal (limited to the first 100 points)
                num_points_to_show = 500  # Set the number of points to display
                fft_values = np.fft.fft(df[column_name])
                frequency = np.fft.fftfreq(len(fft_values))
                positive_values = np.abs(fft_values)
                positive_frequencies = frequency[:num_points_to_show]  # Limit the x-axis
                positive_amplitudes = positive_values[:num_points_to_show]

                axs[1].set_title(f'FFT of the signal - "Wavelength" {i + 1} in the file {archivo}')
                axs[1].semilogy(positive_frequencies, positive_amplitudes)
                axs[1].set_xlabel('Frequency (Hz)')
                axs[1].set_ylabel('Amplitude')
                axs[1].grid()

                plt.tight_layout()
                plt.show()
        else:
            print(f"No se encontraron columnas 'Wavelength' en el archivo {archivo}")
        

        # # Crear DataFrames separados para cada conjunto de datos
        # df_fft = pd.DataFrame(pixel_values)
        # df_pixels = pd.DataFrame(pixels.to_numpy())
        # df_pixel_values = pd.DataFrame(pixel_values)

        # # Guardar los DataFrames en archivos CSV (puedes personalizar los nombres de los archivos de salida)
        # df_fft.to_csv(f'{archivo}_fft.csv', index=False)
        # df_pixels.to_csv(f'{archivo}_pixels.csv', index=False)
        # df_pixel_values.to_csv(f'{archivo}_pixel_values.csv', index=False)





        # # Iterar a través de los picos y crear gráficos individuales
        # for i, peak_index in enumerate(filtered_peaks):
            # # Crear una nueva figura para cada pico
            # plt.figure(figsize=(12, 6))

            # # Obtener el número de columna correspondiente al pico
            # column_name = f'Wavelength {i + 1} [nm]'

            # print(f'Wavelength {i + 1} [nm]')

            # # Graficar la columna correspondiente al pico
            # plt.title(f'Columna correspondiente al Pico en la FFT: {i + 1}')
            # plt.plot(df[column_name])
            # plt.xlabel('Frecuencia (Hz)')
            # plt.ylabel('Amplitud')
            # plt.grid()

            # plt.show()
