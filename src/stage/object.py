import byml
import copy
from dataclasses import dataclass
import json
import os
import uuid
import tempfile
import typing
import time
from typing import List
from google.protobuf import json_format
from src.stage.proto import math_pb2, stage_pb2
from src.stage.serializer import SerializerContext
from src.math import AABB, Vec
from src import sarc_tool
from src.file_format import KCL
from src.config import GlobalConfig

Y_OFFSET = 582 # No clue why this offset is needed by it works

class Object:

    Y_OFFSET = Y_OFFSET

    __next_object_id = 1
    @staticmethod
    def __get_next_object_id():
        obj_id = f'objxx{Object.__next_object_id}'
        Object.__next_object_id += 1
        return obj_id

    def __init__(
        self,
        obj_name: str,
        parameter_config_name: str,
        pos: Vec,
        scale: Vec = Vec(1, 1, 1),
        rot: Vec = Vec(0, 0, 0),
        is_link_dest = False,
        components = [],
        linkset = None,
    ):
        self.__uuid = uuid.uuid1()
        self.__pos = copy.deepcopy(pos)
        self.__components = components
        self.__linkset = linkset

        self.__update_object_file_if_needed(obj_name)

        self._obj_pb = stage_pb2.StageObject()

        self._obj_pb.id = Object.__get_next_object_id()

        self._obj_pb.is_link_dest = is_link_dest

        self._obj_pb.unit_config_name = obj_name
        self._obj_pb.layer_config_name = "Common"
        self._obj_pb.placement_file_name = "WaterfallWorldHomeStage"

        pos += Vec(0, Y_OFFSET, 0)


        self.set_rotation(rot)

        self._obj_pb.scale.x = scale.x()
        self._obj_pb.scale.y = scale.y()
        self._obj_pb.scale.z = scale.z()

        self._obj_pb.translate.x = pos.x()
        self._obj_pb.translate.y = pos.y()
        self._obj_pb.translate.z = pos.z()

        self._obj_pb.unit_config.generate_category = "ObjectList"
        self._obj_pb.unit_config.parameter_config_name = parameter_config_name
        self._obj_pb.unit_config.placement_target_file = "Map"
        self._obj_pb.unit_config.display_scale.x = 1
        self._obj_pb.unit_config.display_scale.y = 1
        self._obj_pb.unit_config.display_scale.z = 1
        self._obj_pb.unit_config.display_rotate.x = 0
        self._obj_pb.unit_config.display_rotate.y = 0
        self._obj_pb.unit_config.display_rotate.z = 0
        self._obj_pb.unit_config.display_translate.x = 0
        self._obj_pb.unit_config.display_translate.y = 0
        self._obj_pb.unit_config.display_translate.z = 0
        
        self._obj_pb.event_wait_action_name = "Wait"

    def uuid(self):
        return self.__uuid
    
    def linkset(self):
        if self.__linkset is None:
            self.__linkset = LinkSet()
        return self.__linkset
    
    def is_link_dest(self):
        return self._obj_pb.is_link_dest
    
    def set_comment(self, comment: str):
        self._obj_pb.unit_config.display_name = comment
    
    def set_is_link_dest(self, is_link_dest: bool):
        self._obj_pb.is_link_dest = is_link_dest

    def to_proto(self, ctx: SerializerContext):
        self._obj_pb.components.extend([component.to_proto(ctx) for component in self.__components])
        if self.name() != 'GroupView': # Prevent infinite recursion on view group since it's a default link
            self._obj_pb.links.CopyFrom(self.linkset().to_proto(ctx))
        return self._obj_pb
    
    def name(self):
        return self._obj_pb.unit_config_name
    
    def get_parameter_config_name(self):
        return self._obj_pb.unit_config.parameter_config_name
    
    def pos(self):
        return self.__pos + Vec(0, Y_OFFSET - 400, 0)
    
    def rotation(self):
        return Vec(
            self._obj_pb.rotate.x,
            self._obj_pb.rotate.y,
            self._obj_pb.rotate.z,
        )
    
    def set_rotation(self, rot: Vec):
        self._obj_pb.rotate.x = rot.x()
        self._obj_pb.rotate.y = rot.y()
        self._obj_pb.rotate.z = rot.z()
    
    def add_component(self, component):
        self.__components.append(component)

    def get_collision(self):
        return ObjectFactory.get_collision(self.name())
    
    def test_collision(self, sphere_center: Vec, sphere_radius: Vec):
        adjusted_sphere_center = sphere_center - self.pos() # Shift sphere center to compensate for translation on object, since collision geometry assumes the object is at the origin
        return self.get_collision().intersects(adjusted_sphere_center, sphere_radius)
    
    __OBJECTS_UPDATED = set()
    def __update_object_file_if_needed(self, obj_name: str):
        if obj_name in Object.__OBJECTS_UPDATED:
            return
        if GlobalConfig.args is None:
            return
        if os.path.exists(os.path.join(GlobalConfig.args.output_romfs_path, f'ObjectData/{obj_name}.szs')):
            # Object file has already been updated in output destination, so no need to re-generate it.
            # Saves a lot of time when generating new seeds, which is the most common use case, 
            # but if you edit object files or edit this updating script, you must remove the object files 
            # from the output romfs path otherwise they won't be re-generated correctly
            return
        if not os.path.exists(os.path.join(GlobalConfig.args.input_romfs_path, f'ObjectData/{obj_name}.szs')):
            return
        
        Object.__OBJECTS_UPDATED.add(obj_name)
        print(f'Updating pose on {obj_name}...')

        def extract_szs(input_file: str, output_dir: str):
            sarc_tool.main(['-o', output_dir, input_file])

        with tempfile.TemporaryDirectory() as tmpdir:
            extract_szs(os.path.join(GlobalConfig.args.input_romfs_path, f'ObjectData/{obj_name}.szs'), tmpdir)
            
            def convert_byml_to_yaml(input_file: str):
                with open(input_file, 'rb') as f:
                    parser = byml.Byml(bytearray(f.read()))
                    return parser.parse()
                
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
            
            yml = convert_byml_to_yaml(os.path.join(tmpdir, 'InitPose.byml'))
            yml['Pose'] = 'TQSV' # Needed for KeyMoveMapParts to prevent quaternion slerp crash
            convert_yaml_to_byml(yml, os.path.join(tmpdir, 'InitPose.byml'))


            yml = convert_byml_to_yaml(os.path.join(tmpdir, 'InitClipping.byml'))
            if 'Radius' in yml:
                yml = {'Radius': byml.byml.Float(5 * yml['Radius'])}
            convert_yaml_to_byml(yml, os.path.join(tmpdir, 'InitClipping.byml'))

            pack_szs(tmpdir, os.path.join(GlobalConfig.args.output_romfs_path, f'ObjectData/{obj_name}.szs'))

            print(f'Updated pose to TQSV on {obj_name}')


VIEW_GROUP_OBJ = Object(
    'GroupView',
    parameter_config_name='GroupView',
    pos = Vec(-8096.37255859375, 22250.0, 5126.52392578125),
)

class Components:

    class Component:

        def __init__(self):
            self._pb = None

        def to_proto(self, ctx: SerializerContext):
            return self._pb

    class StageChange(Component):
        
        def __init__(self, change_stage_id: str):
            pb = stage_pb2.StageChangeComponent(
                change_stage_name = change_stage_id,
                change_stage_id = change_stage_id,
                hint_priority = 0,
                is_connect_to_collision = False,
                is_exit_only = False,
                is_moon = False,
                is_no_shadow = False,
                is_return_prev_stage = False,
                is_valid_entrance_camera = False,
            )
            self._pb = stage_pb2.Component(
                stage_change = pb,
            )

    class KeyMoveNext(Component):

        @dataclass
        class Key:
            pos: Vec = Vec(0,0,0)
            speed: float = 1
            wait_time: int = 1

        def __init__(self, key: Key):
            pb = stage_pb2.KeyMoveNextComponent(
                delay_time = 0,
                interpolate_type = 0,
                is_floor_touch_start = False,
                is_hip_drop_start = False,
                is_play_sign = False,
                is_stop_kill = False,
                move_type = 0,
                speed = key.speed,
                speed_by_time = -1,
                wait_time = key.wait_time,
            )
            self._pb = stage_pb2.Component(
                key_move_next = pb,
            )

    class MoveNext(Component):

        @dataclass
        class Key:
            pos: Vec = Vec(0,0,0)
            delay_frame_num: int = 0
            rail_move_speed: float = 1
            wait_frame_num: int = 1

        def __init__(self, key: Key):
            pb = stage_pb2.MoveNextComponent(
                delay_frame_num = key.delay_frame_num,
                is_wave_check_on = False,
                rail_move_frame = 0,
                rail_move_speed = key.rail_move_speed,
                stage_start_hack = False,
                wait_frame_num = key.wait_frame_num,
            )
            self._pb = stage_pb2.Component(
                move_next = pb,
            )

    class Rail(Component):

        def __init__(self, rail_points: List[Object], rail_type: str, is_closed: bool, is_ladder: bool):
            pass
            self.__rail_points = rail_points
            self.__rail_type = rail_type
            self.__is_closed = is_closed
            self.__is_ladder = is_ladder

        def to_proto(self, ctx: SerializerContext):
            pb = stage_pb2.RailComponent(
                rail_points = [rail_point.to_proto(ctx) for rail_point in self.__rail_points],
                rail_type = self.__rail_type,
                is_closed = self.__is_closed,
                is_ladder = self.__is_ladder,
            )
            return stage_pb2.Component(
                rail = pb,
            )

    class RailPoint(Component):

        def __init__(self, pos: Vec):
            pass
            pos_pb = math_pb2.Vec3(x=pos.x(), y=pos.y(), z=pos.z())
            pb = stage_pb2.RailPointComponent(
                control_points = [pos_pb, pos_pb],
            )
            self._pb = stage_pb2.Component(
                rail_point = pb,
            )

    class NextKey(Component):

        def __init__(self):
            pb = stage_pb2.NextKeyComponent(
                play_step = -1,
                is_keep_pre_self_pose_next_camera = False,
            )
            self._pb = stage_pb2.Component(
                next_key = pb,
            )

    class Capture(Component):

        def __init__(self, cap_name = ''):
            pb = stage_pb2.CaptureComponent(
                cap_name = cap_name,
                is_force_revive_on_dead = True,
                is_revive = True,
                move_type = 1,
                shadow_length = 1500,
            )
            self._pb = stage_pb2.Component(
                capture = pb,
            )

    class CapSwitch(Component):

        def __init__(self):
            pb = stage_pb2.CapSwitchComponent(
                is_connect_to_collision=False,
                is_no_reaction=False, 
                is_valid_object_camera=True, 
                shadow_flag=True,
            )
            self._pb = stage_pb2.Component(
                cap_switch = pb,
            )

    class RiseMapPartsHolder(Component):

        def __init__(self):
            pb = stage_pb2.RiseMapPartsHolderComponent(
                delay_frame=-1, 
                is_valid_object_camera=True, 
                related_boss=-1, 
                reset_first_pos_in_mini_game=False, 
                scenario_no=-1
            )
            self._pb = stage_pb2.Component(
                rise_map_parts_holder = pb,
            )

    class RiseParts(Component):

        @dataclass
        class Key:
            pos: Vec = Vec(0,0,0)
            is_play_success_se: bool = False
            pad_rumble_type: int = -1
            speed: int = 10
            speed_by_time: int = -1
            wait_time: int = -1

    

        def __init__(self, key: Key):
            pb = stage_pb2.RisePartsComponent(
                is_play_success_se=key.is_play_success_se,
                move_interpole_type=0,
                pad_rumble_type=key.pad_rumble_type,
                speed=key.speed,
                speed_by_time=key.speed_by_time,
                wait_time=key.wait_time,
            )
            self._pb = stage_pb2.Component(
                rise_parts = pb,
            )

    class CapRackTimer(Component):

        def __init__(self, duration_in_frames: int):
            pb = stage_pb2.CapRackTimerComponent(
                camera_end_interp_frame=30,
                camera_start_interp_frame=45,
                cap_return_message=0,
                is_connect_to_collision=False,
                is_no_reaction=False,
                is_valid_object_camera=False,
                valid_frame = duration_in_frames
            )
            self._pb = stage_pb2.Component(
                cap_rack_timer = pb,
            )

class LinkSet:

    def __init__(self, 
                debug: List[Object] = [],
                view_group: List[Object] = [VIEW_GROUP_OBJ],
                look_at_rail: List[Object] = [],
                next_key: List[Object] = [],
                no_delete__shine: List[Object] = [],
                switch_alive_keep_on: List[Object] = [],
                key_move_next: List[Object] = [],
                move_next: List[Object] = [],
                rail: List[Object] = [],
                cap_attack_on: List[Object] = [],
                switch_start: List[Object] = [],
                rise_parts: List[Object] = [],
                switch_appear_target: List[Object] = [],
                group_clipping: List[Object] = [],
                camera_switch_on: List[Object] = [],
                switch_appear: List[Object] = [],
                player_restart_pos: List[Object] = [],
                ):
        self.debug = debug
        self.view_group = view_group
        self.look_at_rail = look_at_rail
        self.next_key = next_key
        self.no_delete__shine = no_delete__shine
        self.switch_alive_keep_on = switch_alive_keep_on
        self.key_move_next = key_move_next
        self.move_next = move_next
        self.rail = rail
        self.cap_attack_on = cap_attack_on
        self.switch_start = switch_start
        self.rise_parts = rise_parts
        self.switch_appear_target = switch_appear_target
        self.group_clipping = group_clipping
        self.camera_switch_on = camera_switch_on
        self.switch_appear = switch_appear
        self.player_restart_pos = player_restart_pos

    def to_proto(self, ctx: SerializerContext):
        def convert(objects: List[Object]):
            return [obj.to_proto(ctx) for obj in objects]

        d = vars(self)
        o = {}
        for key in d:
            o[key] = convert(d[key])
        return stage_pb2.LinkSet(
            **o,
        )

class ObjectFactory:

    __COLLISION_CACHE = {}

    @staticmethod
    def get_collision(obj_name: str):
        if obj_name in ObjectFactory.__COLLISION_CACHE:
            return ObjectFactory.__COLLISION_CACHE[obj_name]

        if GlobalConfig.args is None:
            return None

        def extract_szs(input_file: str, output_dir: str):
            sarc_tool.main(['-o', output_dir, input_file])

        def get_collision_data(filepath):
            if not filepath.endswith('.szs'):
                return None
            if not os.path.exists(filepath):
                return None
            with tempfile.TemporaryDirectory() as tmpdir:
                extract_szs(filepath, tmpdir)
                collision_data = None
                for kcl_file in os.listdir(tmpdir):
                    if not kcl_file.endswith('.kcl'):
                        continue
                
                    new_collision_data = KCL.get_collision_data(os.path.join(tmpdir, kcl_file))
                    if collision_data is None:
                        collision_data = new_collision_data
                    else:
                        collision_data = collision_data.union(new_collision_data)
                return collision_data

        collision = get_collision_data(os.path.join(GlobalConfig.args.input_romfs_path, f'ObjectData/{obj_name}.szs'))
        ObjectFactory.__COLLISION_CACHE[obj_name] = collision
        return collision
    
    @staticmethod
    def create_debug_viz(obj_name: str,
                             pos: Vec,
                             debug_links: List[Object] = [],
                             scale: Vec = Vec(1, 1, 1),
                             rot: Vec = Vec(0, 0, 0)):
        return Object(obj_name, parameter_config_name='FixMapParts', pos=pos, scale=scale, rot=rot, linkset=LinkSet(debug=debug_links))

    @staticmethod
    def create_fix_map_parts(obj_name: str,
                             pos: Vec,
                             scale: Vec = Vec(1, 1, 1),
                             rot: Vec = Vec(0, 0, 0)):
        return Object(obj_name, parameter_config_name='FixMapParts', pos=pos, scale=scale, rot=rot)

    @staticmethod
    def create_stage_change_pipe(change_stage_id: str, pos: Vec):
        components = [Components.StageChange(change_stage_id = change_stage_id)]
        return Object('DokanStageChange', parameter_config_name='DokanStageChange', pos=pos, components=components)
    
    @staticmethod
    def create_key_move_parts(obj_name: str, key1: Components.KeyMoveNext.Key, key2: Components.KeyMoveNext.Key):
        link = Object(obj_name, 
                      parameter_config_name='KeyMoveMapParts', 
                      pos=key2.pos, 
                      components=[Components.KeyMoveNext(key2), Components.StageChange('')],
                      is_link_dest=True)
        linkset = LinkSet(key_move_next=[link])
        return Object(obj_name, 
                      parameter_config_name='KeyMoveMapParts', 
                      pos=key1.pos, 
                      components=[Components.KeyMoveNext(key1), Components.StageChange('')],
                      linkset=linkset)
    
    @staticmethod
    def create_move_next(obj_name: str, parameter_config_name: str, key1: Components.MoveNext.Key, key2: Components.MoveNext.Key):
        link = Object(obj_name, 
                      parameter_config_name=parameter_config_name, 
                      pos=key2.pos, 
                      components=[Components.MoveNext(key2)],
                      is_link_dest=True)
        linkset = LinkSet(move_next=[link])
        return Object(obj_name, 
                      parameter_config_name=parameter_config_name, 
                      pos=key1.pos, 
                      components=[Components.MoveNext(key1)],
                      linkset=linkset)
    
    @staticmethod
    def create_rail(rail_points: List[Vec], rail_type='Linear', is_closed=False, is_ladder=False):
        rail_point_objs = [
            Object('Point', parameter_config_name='Point', pos=pos, components=[Components.RailPoint(pos)])
            for pos in rail_points
        ]
        rail = Object('Rail', parameter_config_name='Rail', pos=rail_points[0], is_link_dest=True, components=[Components.Rail(rail_point_objs, rail_type, is_closed, is_ladder)])
        return rail
    
    @staticmethod
    def create_next_key(look_at_rail: Object):
        next_key = Object('ScenarioStartCameraRailMove', parameter_config_name='ScenarioStartCameraRailMove', pos=look_at_rail.pos(), is_link_dest=True, components=[Components.NextKey()], linkset=LinkSet(look_at_rail=[look_at_rail]))
        return next_key
    
    @staticmethod
    def create_stage_switch(pos=Vec(0,0,0)):
        return Object('StageSwitch', parameter_config_name='StageSwitch', pos=pos, is_link_dest=True)

    @staticmethod
    def create_rise_map_parts(obj_name: str, key1: Components.RiseParts.Key, key2: Components.RiseParts.Key):
        link = Object(obj_name, 
                      parameter_config_name='RiseMapParts', 
                      pos=key2.pos, 
                      components=[Components.RiseParts(key2)],
                      is_link_dest=True)
        linkset = LinkSet(key_move_next=[link])
        return Object(obj_name, 
                      parameter_config_name='RiseMapParts', 
                      pos=key1.pos, 
                      components=[Components.RiseParts(key1)],
                      linkset=linkset,
                      is_link_dest=True)

    @staticmethod
    def create_rise_map_parts_holder(stage_switch: Object, rise_parts: Object, pos=Vec(0,0,0)):
        return Object('RiseMapPartsHolder', parameter_config_name='RiseMapPartsHolder', pos=pos, components=[Components.RiseMapPartsHolder()], linkset=LinkSet(view_group=[], switch_start=[stage_switch], rise_parts=[rise_parts]))

    @staticmethod
    def create_cap_switch(pos: Vec, stage_switch: Object):
        return Object('CapSwitchSave', parameter_config_name='CapSwitchSave', pos=pos, components=[Components.CapSwitch()], linkset=LinkSet(cap_attack_on=[stage_switch]))
    
    @staticmethod
    def create_cap_rack_timer(pos: Vec, duration_in_frames: int):
        return Object('CapRackTimer', parameter_config_name='CapRackTimer', pos=pos, components=[Components.CapRackTimer(duration_in_frames=duration_in_frames)])
    
    @staticmethod
    def create_trample_switch_timer(pos: Vec, duration_in_frames: int):
        return Object('TrampleSwitchTimer', parameter_config_name='TrampleSwitchTimer', pos=pos, components=[Components.CapRackTimer(duration_in_frames=duration_in_frames)])
