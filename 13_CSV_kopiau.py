import os
import shutil
import argparse

# Funkzioa fitxategiak kopiatzeko karpeta batean
def copy_files_to_destination(source_folders, destination_folder):
    # Kopiatzeko karpeta sortu, ez bada existitzen
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Ibilbidean joan for-sentziaz
    for source_folder in source_folders:
        # Egiaztatu for-namedikoa existitzen dela
        if os.path.exists(source_folder):
            # Ibilbidean joan eta fitxategiak lortu
            for root, _, files in os.walk(source_folder):
                for filename in files:
                    # Egiaztatu fitxategia 'IIS3DWB_ACC.csv' izena duela
                    if filename == 'IIS3DWB_ACC.csv':
                        source_file = os.path.join(root, filename)
                        destination_file = os.path.join(destination_folder, os.path.basename(source_folder) + '_' + filename)
                        
                        # Fitxategia kopiatu karpeta deestinora
                        shutil.copy(source_file, destination_file)
        else:
            print(f"{source_folder} karpeta ez da existitzen.")

# Komando lerroko argumentuak parseatu
parser = argparse.ArgumentParser(description='Kopiatu CSV fitxategiak hainbat karpetetatik helmuga karpeta batera.')
parser.add_argument('source_folders', type=str, nargs='+', help='Jatorrizko karpeta izenak')
parser.add_argument('destination_folder', type=str, help='Helmuga karpeta izena')
args = parser.parse_args()

# Kopiatu fitxategiak helmuga karpeta batera
copy_files_to_destination(args.source_folders, args.destination_folder)
