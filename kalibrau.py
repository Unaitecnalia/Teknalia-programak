import pandas as pd
import matplotlib.pyplot as plt

# Leer el primer archivo CSV con delimitador de tabulador
archivo_ensayo = "SENSOR 2 TEST 2_ensayo.csv"
df_ensayo = pd.read_csv(archivo_ensayo, delimiter='\t')

# Leer el segundo archivo CSV con delimitador ; y coma como separador decimal
archivo_galgas = "TEST5_galgas.csv"
df_galgas = pd.read_csv(archivo_galgas, delimiter=';', decimal=',')

# Seleccionar las columnas específicas para la calibración
columnas_galgas = ["G1 - CENTRO SUP [?m/m]", "G2 - CENTRO SUP [?m/m]", "G3 - CENTRO INF [?m/m]",
                   "G4 - CENTRO INF [?m/m]", "G5 - LAT SUP [?m/m]", "G6 - LAT INF [?m/m]"]

# Realizar la calibración y graficar para cada columna en una figura separada
for columna_galgas in columnas_galgas:
    calibracion = pd.merge(df_ensayo[["Wavelength 1 [nm]"]], df_galgas[[columna_galgas]], left_index=True, right_index=True)
    
    # Crear una nueva figura para cada columna
    plt.figure(figsize=(8, 5))
    
    # Graficar los datos en 2D con línea más fina
    plt.plot(calibracion["Wavelength 1 [nm]"], calibracion[columna_galgas], label=columna_galgas, linewidth=0.8)
    
    # Configurar el gráfico
    plt.xlabel("Wavelength 1 [nm]")
    plt.ylabel("Valor")
    plt.title(f"Calibración de {columna_galgas}")
    plt.legend()
    plt.grid(True)
    
    # Guardar la figura como PNG sin los últimos 6 caracteres
    nombre_archivo_png = f"calibracion_{archivo_ensayo.replace('.csv','')}_{archivo_galgas.replace('.csv','')}_{columna_galgas.replace(' ', '_')}"
    nombre_archivo_png = nombre_archivo_png[:-7] + ".png"
    plt.savefig(nombre_archivo_png)
    
    # Mostrar la figura actual
    plt.show()

    print(f"Figura guardada como {nombre_archivo_png}")
