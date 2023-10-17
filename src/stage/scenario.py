from src.stage.proto import stage_pb2, math_pb2
from src.stage.area import DeathArea, CameraArea
from src.stage.object import Object
from src.stage.scenario_start_camera import ScenarioStartCamera
from src.stage.player_start_info import Odyssey
from src.stage.serializer import SerializerContext
from src.math import Vec

class Scenario:

    def __init__(self, sky_name = 'CloudWaterFallsBlue', default_data = True):
        self.__areas = []
        self.__objects = []
        self.__zones = []
        self.__sky_name = sky_name
        self.__default_data = default_data
    
    def add_area(self, area):
        self.__areas.append(area)

    def add_object(self, obj):
        self.__objects.append(obj)

    def add_zone(self, zone):
        self.__zones.append(zone)

    def get_zones(self):
        return self.__zones

    def to_proto(self, ctx: SerializerContext):
        scenario_pb = stage_pb2.Scenario()

        player = stage_pb2.Player(
            id = ctx.get_next_object_id(),
            change_stage_id = 'start',
            is_invalidate_cap = False,
            is_link_dest = False,
            is_long_shadow = False,
            is_moon = False,
            model_name = None,
            placement_file_name = 'WaterfallWorldHomeStage',
            unit_config_name = 'PlayerActorHakoniwa',
        )
        player.scale.x = 1
        player.scale.y = 1
        player.scale.z = 1
        player.rotate.x = 0
        player.rotate.y = 0
        player.rotate.z = 0
        player.translate.x = ctx.get_player_start_pos().x()
        player.translate.y = ctx.get_player_start_pos().y()
        player.translate.z = ctx.get_player_start_pos().z()
        player.unit_config.generate_category = 'PlayerList'
        player.unit_config.parameter_config_name = 'PlayerActorHakoniwa'
        player.unit_config.placement_target_file = 'Map'
        player.unit_config.display_scale.x = 1
        player.unit_config.display_scale.y = 1
        player.unit_config.display_scale.z = 1
        player.unit_config.display_rotate.x = 0
        player.unit_config.display_rotate.y = 0
        player.unit_config.display_rotate.z = 0
        player.unit_config.display_translate.x = 0
        player.unit_config.display_translate.y = 0
        player.unit_config.display_translate.z = 0
        scenario_pb.player_list.extend([player])

        scenario_pb.object_list.extend([obj.to_proto(ctx) for obj in self.__objects])

        scenario_pb.area_list.extend([area.to_proto(ctx) for area in self.__areas])

        if self.__default_data:
            scenario_pb.player_start_info_list.extend([
                Odyssey(ctx.get_player_start_pos() + Vec(+200000, +1000000, 0)).to_proto(ctx),
                ])

            scenario_pb.scenario_start_camera_list.extend([
                ScenarioStartCamera(pos=Vec(14495.69, 1600, -1414.213), rot=Vec(0,45,0)).to_proto(ctx),
                # ScenarioStartCamera(pos=Vec(-3464.823, 2700, 3535.534), rot=Vec(0,0,0)).to_proto(ctx),
            ])

            sky = stage_pb2.Sky(
                id = ctx.get_next_object_id(),
                force_placement = True,
                is_link_dest = False,
                is_only_cube_map = False,
                layer_config_name = 'Common',
                model_name = None,
                placement_file_name = 'WaterfallWorldHomeStage',
                texture_pattern_id = -1,
                unit_config_name = self.__sky_name,
                comment = None,
                scale = math_pb2.Vec3(x = 1, y = 1, z = 1),
                rotate = math_pb2.Vec3(x = 0, y = 0, z = 0),
                translate = math_pb2.Vec3(x = 0, y = 0, z = 0),
            )
            sky.unit_config.generate_category = 'SkyList'
            sky.unit_config.parameter_config_name = 'Sky'
            sky.unit_config.placement_target_file = 'Map'
            sky.unit_config.display_scale.x = 1
            sky.unit_config.display_scale.y = 1
            sky.unit_config.display_scale.z = 1
            sky.unit_config.display_rotate.x = 0
            sky.unit_config.display_rotate.y = 0
            sky.unit_config.display_rotate.z = 0
            sky.unit_config.display_translate.x = 0
            sky.unit_config.display_translate.y = 0
            sky.unit_config.display_translate.z = 0
            scenario_pb.sky_list.extend([sky])

        scenario_pb.zone_list.extend([
            Object(obj_name=zone.name, parameter_config_name='Zone', pos=zone.base_pos).to_proto(ctx)
            for zone in self.get_zones()])

        return scenario_pb
