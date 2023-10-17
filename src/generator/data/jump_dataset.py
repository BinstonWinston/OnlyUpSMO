import os
from typing import List
import yaml
from google.protobuf import json_format
from src.generator.data.proto import jump_metadata_pb2
from src.math import Vec

class JumpData:

    def __init__(self, name: str, metadata_pb: jump_metadata_pb2.JumpMetadata, mario_trajectory: List[Vec], cappy_trajectory: List[Vec]):
        self.__name = name
        self.__metadata_pb = metadata_pb
        self.__mario_trajectory = mario_trajectory
        self.__cappy_trajectory = cappy_trajectory

    def name(self):
        return self.__name

    def get_description(self):
        return self.__metadata_pb.desc
    
    def get_difficulty(self):
        return self.__metadata_pb.difficulty
    
    def get_mario_trajectory(self):
        return self.__mario_trajectory
    
    def get_cappy_trajectory(self):
        return self.__cappy_trajectory

    @staticmethod
    def from_data_dir(name: str, dir: str):
        metadata_pb = jump_metadata_pb2.JumpMetadata()
        with open(os.path.join(dir, 'metadata.yaml')) as yaml_file:
            yml = yaml.safe_load(yaml_file.read())
            json_format.ParseDict(yml, metadata_pb)
        mario_trajectory = JumpData.__parse_trajectory(os.path.join(dir, 'mario.obj'))
        cappy_trajectory = JumpData.__parse_trajectory(os.path.join(dir, 'cappy.obj'))
        return JumpData(
            name=os.path.basename(dir),
            metadata_pb=metadata_pb,
            mario_trajectory=mario_trajectory,
            cappy_trajectory=cappy_trajectory,
        )
        
    @staticmethod
    def __parse_trajectory(filepath: str):
        trajectory: List[Vec] = []
        with open(filepath) as obj_file:
            lines = obj_file.read().split('\n')
            for line in lines:
                split = line.split(' ')
                if len(split) >= 4 and split[0] == 'v':
                    [x, y, z] = split[1:4]
                    trajectory.append(Vec(float(x), float(y), float(z)))
        return trajectory


class JumpDataset:

    @staticmethod
    def get_all_jumps(capture_type: str = None):
        folder_name = 'Mario' if capture_type is None else capture_type
        jumps = []
        base_dir = os.path.join('src/generator/data/jumps/', folder_name)
        for jump_folder in os.listdir(base_dir):
            jump = JumpData.from_data_dir(
                jump_folder,
                os.path.join(base_dir, jump_folder))
            jumps.append(jump)
        return jumps