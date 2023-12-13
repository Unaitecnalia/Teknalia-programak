import os

# Zehaztu bilatu nahi duzun karpeta-ruta
ruta_carpeta = '.'  

# Bi egunak zehaztu, eremuaren mugak
fecha_inicio = "20231129_12_21_40"
fecha_fin = "20231129_13_02_23"

# Emandako bidea duten karpeta zerrenda hartu
carpetas = os.listdir(ruta_carpeta)

# Emandako egunen tartean dauden karpeta hautatu eta hutsune batez konkatenatu
carpetas_en_rango = " ".join([carpeta for carpeta in carpetas if fecha_inicio <= carpeta <= fecha_fin])

# Emandako egunen tartean dauden karpeta izenak inprimatu lerro zurrunik sartu gabe
print(carpetas_en_rango)
