import os
import yaml
from google.protobuf import json_format
from src.generator.data.proto import kingdom_dataset_pb2

class KingdomDataset:

    @staticmethod
    def get_all_datasets():
        datasets = []
        for file in sorted(os.listdir('src/generator/data/kingdoms')):
            if not file.endswith('.yaml'):
                continue
            kingdom_name = file.split('-')[1].split('.yaml')[0]
            dataset = KingdomDataset.from_yaml(
                kingdom_name,
                os.path.join('src/generator/data/kingdoms', file))
            datasets.append(dataset)
        return datasets

    @staticmethod
    def from_yaml(name: str, path: str):
        with open(path) as yaml_file:
            yml = yaml.safe_load(yaml_file.read())
            dataset_pb = kingdom_dataset_pb2.KingdomDataset()
            json_format.ParseDict(yml, dataset_pb)
            return KingdomDataset(name, dataset_pb)

    def __init__(self, name: str, pb: kingdom_dataset_pb2.KingdomDataset):
        self.__name = name
        self.__pb = pb

    def name(self):
        return self.__name
    
    def get_sky_name(self):
        return self.__pb.sky

    def get_objects(self):
        return self.__pb.objects
    
    def get_captures(self):
        return self.__pb.captures
    
    def get_capture_specific_objects(self):
        return self.__pb.capture_specific_objects