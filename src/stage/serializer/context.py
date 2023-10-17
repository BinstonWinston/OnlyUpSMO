import byml
import json
import os
import sarc_tool
import shutil
import tempfile
from google.protobuf import json_format
from src.math import Vec

class SerializerContext:

    def __init__(self, player_start_pos: Vec):
        self.__player_start_pos = player_start_pos
        self.__next_object_index = 1

    def get_next_object_id(self):
        id = f'objx{self.__next_object_index}'
        self.__next_object_index += 1
        return id

    def get_player_start_pos(self):
        return self.__player_start_pos

    # obj must have to_proto() method
    # TODO enforce via interfaces
    def __to_dict(self, obj):
        def reformat_yml(yml):
            if isinstance(yml, list):
                return [reformat_yml(x) for x in yml]
            elif isinstance(yml, dict):
                keys = list(yml.keys())
                for key in keys:
                    if key == 'components' and isinstance(yml[key], list):
                        for component in yml[key]:
                            for subcomponent in component: # Unwrap proto oneof type
                                yml = {**reformat_yml(component[subcomponent]), **yml} # Merge component dictionaries flat into object dictionary
                    def process_key_word(word: str):
                        if word == '': # Cause by double underscore __ in original key, representing an escape underscore
                            return '_'
                        return word[0].upper() + word[1:]
                    new_key = ''.join([process_key_word(word) for word in key.split('_')])
                    yml[new_key] = reformat_yml(yml.pop(key))
                return yml
            else:
                return yml
        def __process_obj(obj):
            if isinstance(obj, bool):
                return obj
            elif isinstance(obj, int):
                return byml.byml.Int(obj)
            elif isinstance(obj, float):
                return byml.byml.Float(obj)
            elif isinstance(obj, dict):
                for key in obj:
                    obj[key] = __process_obj(obj[key])
                return obj
            elif isinstance(obj, list):
                return [__process_obj(v) for v in obj]
            else:
                return obj
        pb = obj.to_proto(self)
        yml = json_format.MessageToDict(
            pb,
            including_default_value_fields=True,
            preserving_proto_field_name=True)
        return __process_obj(reformat_yml(yml))

    def package_map_szs(self, scenario, output_szs_path, stage_name):
        print(output_szs_path)
        with SZSOutputTempDir(output_szs_path) as tmpdir:
            for file in os.listdir('src/stage/base_stage_data'):
                shutil.copy(
                    os.path.join('src/stage/base_stage_data', file),
                    os.path.join(tmpdir, file))

            scenario_yml = self.__to_dict(scenario)
            yml = [scenario_yml for _ in range(14)] # 14 is number of scenarios in Map.byml for Cascade

            convert_yaml_to_byml(yml, os.path.join(tmpdir, f'{stage_name}Map.byml'))

        for zone in scenario.get_zones():
            if zone.scenario is not None: # if referencing an existing zone in the base game, no need to create one
                self.package_map_szs(zone.scenario, os.path.join(os.path.dirname(output_szs_path), f'{zone.name}Map.szs'), zone.name)
    

class SZSOutputTempDir:

    def __init__(self, szs_output_path: str):
        self.szs_output_path = szs_output_path

    def __enter__(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        return self.tmpdir.name

    def __exit__(self, *args):
        pack_szs(self.tmpdir.name, self.szs_output_path)
        self.tmpdir.cleanup()

def pack_szs(input_dir: str, output_file: str):
    out_dir = os.path.dirname(output_file)
    if out_dir != '' and not os.path.exists(out_dir):
        os.makedirs(os.path.dirname(output_file))
    sarc_tool.main(['-o', output_file, '-compress', '9', input_dir])

def convert_yaml_to_byml(yml: dict, output_file: str):
    with open(output_file, 'wb+') as f:
        writer = byml.Writer(yml, be=True)
        writer.write(f)