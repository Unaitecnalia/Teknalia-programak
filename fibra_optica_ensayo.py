import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

archivos_ensayo = [archivo for archivo in os.listdir() if "ensayo" in archivo.lower() and archivo.endswith(".csv")]

for archivo in archivos_ensayo:
    df = pd.read_csv(archivo, delimiter='\t')
    
    columns_to_extract = ["Time", "Wavelength 1 [nm]", "Wavelength 2 [nm]"]

    for columna in columns_to_extract:
        if columna == "Time":
            try:
                # Convert 'Time' column to datetime
                datetime_column = pd.to_datetime(df["Time"], format='%I:%M:%S %p')
                # Convert datetime to seconds and normalize, then convert to integer
                time_column = (datetime_column - datetime_column.iloc[0]).dt.total_seconds().astype(int).values

                # Print the length of the converted 'Time' column
                print(f"Length of {columna}: {len(time_column)}")
                # Print the converted 'Time' column without the decimal point
                print(f"{columna} in seconds: {time_column}")
            except Exception as e:
                print(f"Error converting {columna}: {e}")
                continue
        else:
            try:
                # Convert data column to numeric
                data = pd.to_numeric(df[columna], errors='coerce').values
                if np.isnan(data).any():
                    print(f"Warning: Some data in the column {columna} is not numeric.")
            except Exception as e:
                print(f"Error converting {columna}: {e}")
                continue

            # Debugging message to ensure it enters the else block
            print(f"Processing {columna} in the else block")

            # Continue with the rest of the processing
            fft_result = np.fft.fft(data)
            fs = 10  # Frecuencia de muestreo de 10 Hz
            fft_frequencies = np.fft.fftfreq(len(data), d=1/fs)

            # Tomar solo los valores positivos de la FFT en el eje x
            fft_frequencies = np.abs(fft_frequencies)

            # Calcular el valor medio del Wavelength
            wavelength_medio = np.mean(pd.to_numeric(df[columna], errors='coerce'))

            fig, axs = plt.subplots(2, 1, figsize=(10, 8))

            axs[0].plot(time_column, data)
            axs[0].set_title(f'{columna} - Wavelength Medio: {wavelength_medio:.2f} nm')
            axs[0].set_xlabel('Tiempo (s)')  # Etiqueta del eje x en el primer subplot

            axs[1].semilogy(fft_frequencies, np.abs(fft_result))
            axs[1].set_title(f'FFT - {columna}')
            axs[1].set_xlabel('Frecuencia (Hz)')  # Etiqueta del eje x en el segundo subplot
            axs[1].set_xlim(0, 0.04 * max(fft_frequencies))  # Establecer límites del eje x en el segundo subplot
            # axs[1].set_xlim(0, 0.2)  # Establecer límites del eje x en el segundo subplot

            # Guardar el gráfico como una imagen con un identificador único
            output_image_path = f"{archivo}_{columna.replace(' ', '_')}.png"
            plt.savefig(output_image_path)

            plt.tight_layout()
            plt.show()
