import os
import shutil
import struct

class BFRES:

    @staticmethod
    def rename(input_path: str, output_path: str):
        shutil.move(input_path, output_path)
        input_name = os.path.basename(input_path).replace('.bfres', '')
        output_name = os.path.basename(output_path).replace('.bfres', '')

        file_name_offset = None
        with open(output_path, 'rb') as file:
            # Format spec https://mk8.tockdom.com/wiki/BFRES_(File_Format)
            file.seek(0x14-4)
            file_name_offset, = struct.unpack('<i', file.read(4))

        with open(output_path, 'r+b') as file:
            # Format spec https://mk8.tockdom.com/wiki/BFRES_(File_Format)
            file.seek(file_name_offset)
            file.write(bytes([0] * len(input_name))) # Clear input name
            file.seek(file_name_offset)
            file.write(bytes(output_name, 'UTF-8'))

        