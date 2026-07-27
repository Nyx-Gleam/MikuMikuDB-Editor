# import os
# import subprocess
# import sys
# import glob
# 
# def convert_vag_to_wav(input_folder):
#     # Verifica que la carpeta exista
#     if not os.path.isdir(input_folder):
#         print("Error: La ruta no es una carpeta válida.")
#         return
#     
#     # Crea la carpeta de salida: mismo nombre + "_wav"
#     folder_name = os.path.basename(os.path.normpath(input_folder))
#     parent_folder = os.path.dirname(os.path.normpath(input_folder))
#     output_folder = os.path.join(parent_folder, f"{folder_name}_wav")
#     
#     # Crea la carpeta si no existe
#     os.makedirs(output_folder, exist_ok=True)
#     print(f"Carpeta de salida creada: {output_folder}")
#     
#     # Busca archivos .vag (mayúsculas y minúsculas)
#     vag_files = glob.glob(os.path.join(input_folder, "*.vag")) + \
#                 glob.glob(os.path.join(input_folder, "*.VAG"))
#     
#     if not vag_files:
#         print("No se encontraron archivos .vag en la carpeta.")
#         return
#     
#     print(f"Se encontraron {len(vag_files)} archivos .vag. Iniciando conversión...\n")
#     
#     for vag_file in vag_files:
#         # Nombre del archivo sin extensión
#         base_name = os.path.splitext(os.path.basename(vag_file))[0]
#         wav_file = os.path.join(output_folder, f"{base_name}.wav")
#         
#         # Comando FFmpeg: conversión directa a WAV (sin parámetros extra, calidad original)
#         command = ["ffmpeg", "-i", vag_file, wav_file]
#         try:
#             subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             print(f"✓ Convertido: {os.path.basename(vag_file)} → {base_name}.wav")
#         except subprocess.CalledProcessError as e:
#             error_msg = e.stderr.decode().strip()
#             print(f"✗ Error al convertir {os.path.basename(vag_file)}:\n{error_msg}")
#         except FileNotFoundError:
#             print("Error: FFmpeg no está instalado o no está en el PATH.")
#             print("Descárgalo de https://ffmpeg.org/download.html y agrégalo al PATH.")
#             return
#         
#         print(f"\n¡Conversión completada! Todos los WAV están en: {output_folder}")
#             
# if __name__ == "__main__":
#     # Si pasas la carpeta como argumento en la terminal
#     if len(sys.argv) > 1:
#         folder = sys.argv[1].strip('"') # Quita comillas si copias y pegas ruta en Windows
#     else:
#         folder = input("Ingresa la ruta completa de la carpeta con los .vag: ").strip('"')
#     
#     convert_vag_to_wav(folder)



import os
import subprocess
import sys
import glob

def convert_with_vgmstream(input_folder, vgmstream_path="vgmstream-cli.exe"):
    if not os.path.isdir(input_folder):
        print("Error: La ruta no es una carpeta válida.")
        return
    
    if not os.path.isfile(vgmstream_path):
        print(f"Error: No se encuentra {vgmstream_path}. Colócalo en la misma carpeta que este script o indica la ruta completa.")
        return
    
    # Carpeta de salida
    folder_name = os.path.basename(os.path.normpath(input_folder))
    parent_folder = os.path.dirname(os.path.normpath(input_folder))
    output_folder = os.path.join(parent_folder, f"{folder_name}_wav")
    
    os.makedirs(output_folder, exist_ok=True)
    print(f"Carpeta de salida: {output_folder}")
    
    # Busca .vag
    vag_files = glob.glob(os.path.join(input_folder, "*.vag")) + \
                glob.glob(os.path.join(input_folder, "*.VAG"))
    
    if not vag_files:
        print("No se encontraron archivos .vag.")
        return
    
    print(f"Se encontraron {len(vag_files)} archivos. Iniciando conversión...\n")
    
    for vag_file in vag_files:
        base_name = os.path.splitext(os.path.basename(vag_file))[0]
        wav_file = os.path.join(output_folder, f"{base_name}.wav")
        
        # Comando: vgmstream-cli -i (ignore loop) -o output.wav input.vag
        command = [vgmstream_path, "-i", "-o", wav_file, vag_file]
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✓ Convertido: {os.path.basename(vag_file)} → {base_name}.wav")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode().strip()
            print(f"✗ Error en {os.path.basename(vag_file)}:\n{error_msg}")
        except FileNotFoundError:
            print("Error: vgmstream-cli no encontrado.")
            return
        
        print(f"\n¡Listo! WAVs en: {output_folder}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder = sys.argv[1].strip('"')
    else:
        folder = input("Ruta de la carpeta con .vag: ").strip('"')
        
        # Asume que vgmstream-cli.exe está en la misma carpeta que el script
        convert_with_vgmstream(folder)