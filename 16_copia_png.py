import os
import shutil

# Bilaketa egiteko hasierako eta amaierako karpeta-izenak
hasierako_karpeta_izena = "20231117_10_44_16"
amaierako_karpeta_izena = "20231117_11_17_13"

# Helmuga karpeta-izenaren izena
helmuga_karpeta = "copia_png"

# Egiaztatu helmuga karpeta existitzen den, eta bestela, sortu
if not os.path.exists(helmuga_karpeta):
    os.makedirs(helmuga_karpeta)

# Lortu karpeta-izenen zerrenda uneko direktorioan
direktorioan_daude_karpetak = [izena for izena in os.listdir() if os.path.isdir(izena)]

# hasierako_karpeta_izena eta amaierako_karpeta_izena artean dauden karpeta filtratu
karpetak_iragaztuta = [izena for izena in direktorioan_daude_karpetak if hasierako_karpeta_izena <= izena <= amaierako_karpeta_izena]

# Iragaztutako karpetetan iteratu
for karpeta in karpetak_iragaztuta:
    # Lortu PNG fitxategi-izenen zerrenda uneko karpetan
    png_fitxategiak = [fitxategia for fitxategia in os.listdir(karpeta) if fitxategia.lower().endswith('.png')]

    # Kopiatu PNG fitxategiak helmuga karpetara
    for png_fitxategia in png_fitxategiak:
        jatorri_ruta = os.path.join(karpeta, png_fitxategia)
        helmuga_ruta = os.path.join(helmuga_karpeta, png_fitxategia)
        shutil.copy(jatorri_ruta, helmuga_ruta)

print("Prozesua amaituta. PNG fitxategiak 'copia_png' karpetera kopiatuak.")
