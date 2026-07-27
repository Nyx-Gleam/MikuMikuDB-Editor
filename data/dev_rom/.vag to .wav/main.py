"""
VAG to WAV Converter
====================

A standalone utility that converts all .vag audio files in a directory
to .wav format using vgmstream-cli.

Requirements:
    - vgmstream-cli.exe

Author (of this script):
    Nyx-Gleam

License:
    MIT License
"""

import glob
import os
import subprocess
import sys


def convert_with_vgmstream(input_folder, vgmstream_path="vgmstream-cli.exe"):
    """
    Convert all VAG audio files in a folder to WAV format using vgmstream-cli.

    Parameters
    ----------
    input_folder : str
        Path to the folder containing .vag files.
    vgmstream_path : str, optional
        Path to the vgmstream-cli executable.
        Defaults to "vgmstream-cli.exe".

    Returns
    -------
    None
    """
    if not os.path.isdir(input_folder):
        print("Error: The specified path is not a valid directory.")
        return

    if not os.path.isfile(vgmstream_path):
        print(
            f"Error: '{vgmstream_path}' was not found. "
            "Place it in the same folder as this script or specify its full path."
        )
        return

    # Create output directory
    folder_name = os.path.basename(os.path.normpath(input_folder))
    parent_folder = os.path.dirname(os.path.normpath(input_folder))
    output_folder = os.path.join(parent_folder, f"{folder_name}_wav")

    os.makedirs(output_folder, exist_ok=True)
    print(f"Output folder: {output_folder}")

    # Search for .vag files
    vag_files = (
        glob.glob(os.path.join(input_folder, "*.vag"))
        + glob.glob(os.path.join(input_folder, "*.VAG"))
    )

    if not vag_files:
        print("No .vag files were found.")
        return

    print(f"Found {len(vag_files)} file(s). Starting conversion...\n")

    for vag_file in vag_files:
        base_name = os.path.splitext(os.path.basename(vag_file))[0]
        wav_file = os.path.join(output_folder, f"{base_name}.wav")

        # vgmstream-cli -i (ignore loop) -o output.wav input.vag
        command = [vgmstream_path, "-i", "-o", wav_file, vag_file]

        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✓ Converted: {os.path.basename(vag_file)} → {base_name}.wav")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode(errors="ignore").strip()
            print(f"✗ Failed to convert {os.path.basename(vag_file)}:\n{error_msg}")

        except FileNotFoundError:
            print("Error: vgmstream-cli executable was not found.")
            return

    print(f"\nDone! Converted WAV files have been saved to:\n{output_folder}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder = sys.argv[1].strip('"')
    else:
        folder = input("Enter the folder containing .vag files: ").strip('"')

    # Assume vgmstream-cli.exe is located next to this script.
    convert_with_vgmstream(folder)
