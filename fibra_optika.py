import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft
import pandas as pd

# Cargar datos desde el archivo CSV
filename = 'test_5.csv'  # Asegúrate de que el archivo esté en la misma carpeta que este script
data = pd.read_csv(filename, sep='\t')

# Obtener las columnas de tiempo y longitud de onda
time = data['Time [sec]']
wavelength = data['Wavelength 1[nm]']

# Calcular la frecuencia de muestreo (fs) desde el tiempo
time_diff = np.diff(time)
fs = 1.0 / np.mean(time_diff)

# Convertir la serie de datos de longitud de onda a un arreglo NumPy
wavelength_array = wavelength.to_numpy()

# Calcular la FFT
fft_result = fft(wavelength_array)
frequencies = np.fft.fftfreq(len(wavelength_array), d=time_diff[0])

# Eliminar el primer valor de la FFT
# fft_result[0] = 0.0

# Realizar la IFFT
ifft_result = ifft(fft_result)

# Actualizar los valores de longitud de onda con el resultado de la IFFT
data['Wavelength 1[nm]'] = ifft_result.real

# Guardar el DataFrame actualizado en un nuevo archivo CSV
data.to_csv('ifft_result.csv', index=False)

# Mostrar los valores guardados
print("Valores de la IFFT guardados en ifft_result.csv:")
print(data['Wavelength 1[nm]'])

# Encontrar la frecuencia exacta del pico del FFT
max_amplitude_index = np.argmax(np.abs(fft_result))
peak_frequency = frequencies[max_amplitude_index]

# Graficar los valores de longitud de onda y la FFT (limitando a 0-140 Hz)
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(time, wavelength)
plt.xlabel("Tiempo [sec]")
plt.ylabel("Longitud de Onda [nm]")
plt.title("Valores de Longitud de Onda en el Tiempo")

# Establecer el formato del eje Y para mostrar todos los decimales
plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)

plt.subplot(2, 1, 2)
plt.semilogy(abs(frequencies), np.abs(fft_result))
plt.xlabel("Frecuencia [Hz]")
plt.ylabel("Amplitud")
plt.title("Transformada Rápida de Fourier (FFT)")
plt.xlim(0, 140)  # Limitar el rango en el eje x a 0-140 Hz
plt.margins(y=0.1)  # Ajustar los márgenes del eje Y

# Agregar la frecuencia exacta del pico al título del gráfico
plt.text(peak_frequency, np.abs(fft_result[max_amplitude_index]), f"{peak_frequency:.2f} Hz",
         horizontalalignment='left', verticalalignment='bottom')
plt.tight_layout()
plt.show()

# Imprimir la frecuencia de muestreo (fs) y la frecuencia exacta del pico
print(f"Frecuencia de Muestreo (fs): {fs} Hz")
print(f"Frecuencia Exacta del Pico del FFT: {peak_frequency:.2f} Hz")
