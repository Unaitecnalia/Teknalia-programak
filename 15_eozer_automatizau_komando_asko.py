import subprocess
import sys
import os

def ejecutar_comandos(comandos, karpetak):
    for karpeta in karpetak:
        for comando in comandos:
            komando_osorik = f'{comando} {karpeta}'
            subprocess.run(komando_osorik, shell=True)

# Exekutatzeko komandoen zerrenda
# komandoak = ['python 4_bibrazioa_eta_fft_irudia_gorde.py']
# komandoak = ['python 6_Treneko_kolperako_1_5_segundu_2_fft.py']
# komandoak = ['python 6_2_Treneko_kolperako_0_5_segundu.py']
komandoak = ['python 6_3_Treneko_kolperako_0_5_segundu.py']
# komandoak = ['python 10_datalog_automatizau.py', 'python 4_bibrazioa_eta_fft_irudia_gorde.py']
# komandoak = ['python 20_CSV_NanoEdgera_aldatu.py']

# Argibideen zerrenda lortu komandoa exekutatzeko
if len(sys.argv) != 3:
    print("Erabilera: python 15_2_eozer_automatizau_komando_asko.py hasierako_karpeta amaierako_karpeta")
    sys.exit(1)

hasierako_karpeta = sys.argv[1]
amaierako_karpeta = sys.argv[2]

# hasierako_karpeta eta amaierako_karpeta artean dauden karpeta-izenen zerrenda lortu
karpetak = [izena for izena in os.listdir() if os.path.isdir(izena) and hasierako_karpeta <= izena <= amaierako_karpeta]

# Komandoak exekutatu hasierako_karpeta eta amaierako_karpeta artean dauden karpeta guztietarako
ejecutar_comandos(komandoak, karpetak)
