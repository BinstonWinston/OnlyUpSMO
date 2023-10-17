import argparse
from enum import Enum
from typing import List
import sys
import tempfile
import os
import byml
import random
import re

from src import stage
from src.stage.serializer import SerializerContext
from src.generator.data.kingdom_dataset import KingdomDataset
from src.file_format.bfres import BFRES
from src.config import GlobalConfig

import sarc_tool
from src.math import AABB, Vec
from src.generator import Generator

class Difficulty(Enum):
    EASY = 'easy'
    HARD = 'hard'
    ULTRA = 'ultra'

    @staticmethod
    def get_obj_set_count_multiplier(d):
        if d == Difficulty.EASY:
            return 3
        elif d == Difficulty.HARD:
            return 10
        elif d == Difficulty.ULTRA:
            return 7
        else:
            raise Exception(f'Invalid difficulty {d}')
        
    @staticmethod
    def get_y_level_increase_per_object(d):
        if d == Difficulty.EASY:
            return 100
        elif d == Difficulty.HARD:
            return 160
        elif d == Difficulty.ULTRA:
            return 160
        else:
            raise Exception(f'Invalid difficulty {d}')
        
# class GlobalConfig:
#     difficulty = Difficulty.HARD
#     checkpoints_enabled = False

PLAYER_START_POS = Vec(13900, 588 + 20000, 5700)

class DataCache:
    object_index = 1

    @staticmethod
    def clear():
        DataCache.object_index = 1

def generate_stage(kingdom_dataset: KingdomDataset, current_stage_name: str, prev_stage_name: str, next_stage_name: str):
    return Generator(kingdom_dataset).generate(PLAYER_START_POS, current_stage_name, prev_stage_name, next_stage_name)

def extract_szs(input_file: str, output_dir: str):
    sarc_tool.main(['-o', output_dir, input_file])

def pack_szs(input_dir: str, output_file: str):
    out_dir = os.path.dirname(output_file)
    if out_dir != '' and not os.path.exists(out_dir):
        os.makedirs(os.path.dirname(output_file))
    sarc_tool.main(['-o', output_file, '-compress', '9', input_dir])

def convert_byml_to_yaml(input_file: str):
    with open(input_file, 'rb') as f:
        parser = byml.Byml(bytearray(f.read()))
        return parser.parse()
    
def convert_yaml_to_byml(yml: dict, output_file: str):
    with open(output_file, 'wb+') as f:
        writer = byml.Writer(yml, be=True)
        writer.write(f)

class SZSTransformerTempDir:

    def __init__(self, szs_input_path: str, szs_output_path: str):
        self.szs_input_path = szs_input_path
        self.szs_output_path = szs_output_path

    def __enter__(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        extract_szs(self.szs_input_path, self.tmpdir.name)
        return self.tmpdir.name

    def __exit__(self, *args):
        pack_szs(self.tmpdir.name, self.szs_output_path)
        self.tmpdir.cleanup()

def reformat_key(key: str):
    words = re.findall('[A-Z][^A-Z]*', key)
    return "_".join([word.lower() for word in words])

def reformat_yml(yml):
    if isinstance(yml, list):
        return [reformat_yml(x) for x in yml]
    if isinstance(yml, dict):
        keys = list(yml.keys())
        for key in keys:
            yml[reformat_key(key)] = reformat_yml(yml.pop(key))
        return yml
    else:
        return yml
    

def process_stage_map_file(kingdom_dataset: KingdomDataset, output_stage_name: str, prev_stage_name: str, next_stage_name: str):
    scenario = generate_stage(kingdom_dataset, output_stage_name, prev_stage_name, next_stage_name)
    ctx = SerializerContext(PLAYER_START_POS)
    ctx.package_map_szs(
        scenario,
        os.path.join(GlobalConfig.args.output_romfs_path, f'StageData/{output_stage_name}Map.szs'),
        output_stage_name)

def process_stage_sound_file(input_stage_name: str, output_stage_name: str):
    with SZSTransformerTempDir(os.path.join(GlobalConfig.args.input_romfs_path, f'StageData/{input_stage_name}Sound.szs'), os.path.join(GlobalConfig.args.output_romfs_path, f'StageData/{output_stage_name}Sound.szs')) as tmpdir:
        yml = convert_byml_to_yaml(os.path.join(tmpdir, f'{input_stage_name}Sound.byml'))
        yml = [{'AreaList': [], 'ObjectList': []} for _ in yml]
        convert_yaml_to_byml(yml, os.path.join(tmpdir, os.path.join(tmpdir, f'{output_stage_name}Sound.byml')))

def process_stage_design_file(input_stage_name: str, output_stage_name: str):
    with SZSTransformerTempDir(os.path.join(GlobalConfig.args.input_romfs_path, f'StageData/{input_stage_name}Design.szs'), os.path.join(GlobalConfig.args.output_romfs_path, f'StageData/{output_stage_name}Design.szs')) as tmpdir:
        yml = convert_byml_to_yaml(os.path.join(tmpdir, f'{input_stage_name}Design.byml'))
        yml = [{'AreaList': [], 'ObjectList': []} for _ in yml]
        convert_yaml_to_byml(yml, os.path.join(tmpdir, os.path.join(tmpdir, f'{output_stage_name}Design.byml')))

def process_stage_cube_map(input_stage_name: str, output_stage_name: str):
    output_file_path =  os.path.join(GlobalConfig.args.output_romfs_path, f'ObjectData/CubeMap{output_stage_name}.szs')
    if os.path.exists(output_file_path):
        return # Early return to speed up generation time
    print(f'Copying cube map: {input_stage_name} --> {output_stage_name}')
    with SZSTransformerTempDir(os.path.join(GlobalConfig.args.input_romfs_path, f'ObjectData/CubeMap{input_stage_name}.szs', output_file_path)) as tmpdir:
        BFRES.rename(
            os.path.join(tmpdir, f'CubeMap{input_stage_name}.bfres'),
            os.path.join(tmpdir, f'CubeMap{output_stage_name}.bfres'),
        )

def process_stage(kingdom_dataset: KingdomDataset, input_stage_name, output_stage_name, prev_stage_name, next_stage_name):
    process_stage_map_file(kingdom_dataset, output_stage_name, prev_stage_name, next_stage_name)
    process_stage_sound_file(input_stage_name, output_stage_name)
    process_stage_design_file(input_stage_name, output_stage_name)
    process_stage_cube_map(input_stage_name, output_stage_name)

def generate_only_up_stage():
    configs = [
        ('OnlyUpUltra', Difficulty.ULTRA),
    ]

    def get_stage_name(kingdom_dataset: KingdomDataset):
        return f'{stage_name}{kingdom_dataset.name()}Stage'

    kingdom_datasets = KingdomDataset.get_all_datasets()
    for stage_name, difficulty in configs:
        for i in range(len(kingdom_datasets)):
            prev_stage_name = None if i == 0 else get_stage_name(kingdom_datasets[i-1]) # no prev kingdom for first kingdom
            next_stage_name = 'OnlyUpWinStage' if i+1 >= len(kingdom_datasets) else get_stage_name(kingdom_datasets[i+1])
            kingdom_dataset = kingdom_datasets[i]
            random.seed(hash(GlobalConfig.args.seed) + sum([ord(c) for c in stage_name])) # Offset seed by sum of stage name characters so the segment choices are different for each kingdom
            DataCache.clear()
            GlobalConfig.difficulty = difficulty
            process_stage(kingdom_dataset, f'{kingdom_dataset.name()}HomeStage', get_stage_name(kingdom_dataset), prev_stage_name, next_stage_name)
    print('Stage generation done')

def parse_args(args: List[str]):
    parser = argparse.ArgumentParser(
                    prog='SMO OnlyUp Stage Generator',
                    description='Generate procedural OnlyUp-style stages for SMO',
                    epilog='Thanks for trying this project :)')
    parser.add_argument(
        '-o', '--output_romfs_path',
        required=True,
        help='Output directory to place generated stage and object files'
    )
    parser.add_argument(
        '-i', '--input_romfs_path',
        required=True,
        help='A romfs dump of SMO obtained from your copy of SMO, used for reading object collisions'
    )
    parser.add_argument(
        '-s', '--seed',
        type=str,
        required=True,
        help='A string used to seed the random generation. Similar to MineCraft, the same seed will always produce the same level',
    )
    parser.add_argument(
        '--object_collision_debug_dir',
        default=None,
        help='Optional output dir for exporting stage object collisions as .obj files. Should only be necessary if you\'re updating the generation algorithm itself'
    )

    return parser.parse_args(args)

def main(args: List[str]):
    GlobalConfig.args = parse_args(args)
    generate_only_up_stage()

if __name__ == '__main__':
    main(sys.argv[1:])