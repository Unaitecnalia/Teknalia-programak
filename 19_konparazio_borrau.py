import os
import argparse

def delete_comparison_pngs(folders):
    # Karpeten artean iteratu
    for folder in folders:
        # Karpetan dauden fitxategi guztietan iteratu
        for filename in os.listdir(folder):
            # ".png" batekin amaitzen bada eta "konparazio" hitza izan dezakeenean
            if filename.endswith(".png") and "konparazio" in filename:
                # Fitxategiaren bidea osatu
                file_path = os.path.join(folder, filename)
                try:
                    # Fitxategia ezabatu
                    os.remove(file_path)
                    print(f"{file_path} - Ezabatuta")
                except Exception as e:
                    # Ezabatzerakoan errorea gertatu bada, errorea inprimatu
                    print(f"{file_path} - Ezabatzean errorea gertatu da: {e}")

def main():
    # Komando lerroko argumentuak prozesatu
    parser = argparse.ArgumentParser(description="PNG fitxategiak 'konparazio' hitza izan dutenean ezabatu.")
    parser.add_argument("folders", nargs='+', help="Karpeta izenak")
    args = parser.parse_args()

    # Funkzio nagusia deitu argumentu bezala jasotako karpeten zerrendarekin
    delete_comparison_pngs(args.folders)

if __name__ == "__main__":
    # Programa nagusia exekutatzeko
    main()
