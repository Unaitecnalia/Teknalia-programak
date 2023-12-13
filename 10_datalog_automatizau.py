import subprocess
import sys

# Lortu komando-lerroetatik karpeta izenak
carpetas = sys.argv[1:]

# Oinarri komandoa
comando_base = 'python hsdatalog_data_export.py'

# Iteratu karpeta bakoitzeko eta komandoa bakoitzeko exekutatu
for carpeta in carpetas:
    # Eraiki komando osoa
    comando = f'{comando_base} .\\{carpeta} -o .\\{carpeta} -f CSV -s all'
    
    # Exekutatu komandoa cmd-en
    subprocess.run(comando, shell=True)
