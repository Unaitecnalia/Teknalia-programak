import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta

# Leer el primer archivo CSV con delimitador de tabulador
archivo_ensayo = "Fibra5_SENSOR 2 TEST 2_ensayo.csv"
df_ensayo = pd.read_csv(archivo_ensayo, delimiter='\t')

# Leer el segundo archivo CSV con delimitador ; y coma como separador decimal
archivo_galgas = "Galga5_TEST5_galgas.csv"
df_galgas = pd.read_csv(archivo_galgas, delimiter=';', decimal=',')

# Seleccionar la columna específica para la calibración de ensayo
columna_ensayo = "Wavelength 1 [nm]"

# Seleccionar las seis columnas de las galgas para la calibración
columnas_galgas = ["G1 - CENTRO SUP [?m/m]", "G2 - CENTRO SUP [?m/m]", "G3 - CENTRO INF [?m/m]",
                   "G4 - CENTRO INF [?m/m]", "G5 - LAT SUP [?m/m]", "G6 - LAT INF [?m/m]"]

# Cambiar el nombre del label para Fibra Óptica
label_ensayo = "Fibra Óptica"

# Normalizar los puntos del ensayo para que comiencen en 0
min_ensayo = df_ensayo[columna_ensayo].min()
df_ensayo[columna_ensayo] = df_ensayo[columna_ensayo] - min_ensayo

# Normalizar los puntos para que tengan el mismo rango y escala
max_galgas = max(df_galgas[columna].max() for columna in columnas_galgas)
max_ensayo = df_ensayo[columna_ensayo].max()

# Ruta del archivo de valores
archivo_valores = "mejores_valores.txt"

# Verificar si el archivo de valores existe
if os.path.exists(archivo_valores):
    # Leer los valores desde el archivo
    with open(archivo_valores, "r") as file:
        lines = file.readlines()
        for line in lines:
            # Separar el nombre de la variable y el valor
            parts = line.split(":")
            if len(parts) == 2:
                var_name = parts[0].strip()
                var_value = float(parts[1].strip())  # Asegúrate de ajustar el tipo de dato según sea necesario
                # Asignar el valor a la variable correspondiente
                if var_name == "Mejor Desplazamiento Vertical":
                    best_shift_vertical = var_value
                elif var_name == "Mejor Desplazamiento Horizontal":
                    best_shift_horizontal = var_value
                elif var_name == "Mejor Amplitud":
                    best_amplitude = var_value

    # Graficar los 6 plots utilizando los valores leídos
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, columna_galgas in enumerate(columnas_galgas):
        puntos_galgas = df_galgas[columna_galgas] * (max_ensayo / max_galgas)

        # Aplicar los valores leídos al proceso de gráficos
        shifted_ensayo = np.roll(df_ensayo[columna_ensayo], int(best_shift_vertical))
        shifted_ensayo = shifted_ensayo * best_amplitude
        plt.figure(figsize=(8, 5))
        
        # Graficar los datos del ensayo
        plt.plot(df_ensayo.index, shifted_ensayo, label="Fibra óptica (Ensayo)")

        # Graficar los datos de las galgas
        plt.plot(df_galgas.index, puntos_galgas, label=f"{columna_galgas} (Galgas)")

        # Configurar el gráfico
        plt.xlabel("Índice de Tiempo")
        plt.ylabel("Valor")
        plt.title(f"Comparación de {columna_ensayo} y {columna_galgas}")
        plt.legend()
        plt.grid(True)

        # Mostrar la figura actual
        plt.show()
else:
    # Resto de tu código original
    for i, columna_galgas in enumerate(columnas_galgas):
        puntos_galgas = df_galgas[columna_galgas] * (max_ensayo / max_galgas)

        # Calcular la correlación entre el ensayo y la galga actual
        correlation = np.correlate(df_ensayo[columna_ensayo], puntos_galgas, mode='full')
        shift = np.argmax(correlation) - len(df_ensayo) + 1

        if abs(correlation[shift]) > abs(max_correlation):
            max_correlation = correlation[shift]
            best_shift = shift

# Este bloque de código puede estar al final del script
# Imprimir el desplazamiento calculado por pantalla
print(f"Desplazamiento calculado: {best_shift_vertical} puntos (Vertical), {best_shift_horizontal} puntos (Horizontal)")
print(f"Amplitud calculada: {best_amplitude}")

# Guardar los valores en el archivo de valores
with open(archivo_valores, "w") as file:
    file.write(f"Mejor Desplazamiento Vertical: {best_shift_vertical}\n")
    file.write(f"Mejor Desplazamiento Horizontal: {best_shift_horizontal}\n")
    file.write(f"Mejor Amplitud: {best_amplitude}\n")

# Aplicar el mejor desplazamiento a los datos del ensayo
df_ensayo[columna_ensayo] = df_ensayo[columna_ensayo].shift(int(best_shift_vertical), fill_value=0)
