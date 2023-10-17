from src.stage.proto import stage_pb2
from src.stage.serializer import SerializerContext
from src.stage.object import Object, LinkSet
from src.math import Vec

class Area:

    def __init__(self, obj_name: str, model_name: str, pos: Vec, scale: Vec, linkset: LinkSet = None):
        self._linkset = linkset
        self._area_pb = stage_pb2.Area()

        self._area_pb.is_link_dest = False
        self._area_pb.layer_config_name = 'Common'
        self._area_pb.model_name = model_name
        self._area_pb.placement_file_name = 'WaterfallWorldHomeStage'
        self._area_pb.unit_config_name = obj_name
        self._area_pb.priority = -1

        self._area_pb.rotate.x = 0
        self._area_pb.rotate.y = 0
        self._area_pb.rotate.z = 0

        self._area_pb.scale.x = scale.x()
        self._area_pb.scale.y = scale.y()
        self._area_pb.scale.z = scale.z()

        self._area_pb.translate.x = pos.x()
        self._area_pb.translate.y = pos.y()
        self._area_pb.translate.z = pos.z()

        self._area_pb.unit_config.generate_category = 'AreaList'
        self._area_pb.unit_config.parameter_config_name = obj_name
        self._area_pb.unit_config.placement_target_file = 'Map'
        self._area_pb.unit_config.display_scale.x = 1
        self._area_pb.unit_config.display_scale.y = 1
        self._area_pb.unit_config.display_scale.z = 1
        self._area_pb.unit_config.display_rotate.x = 0
        self._area_pb.unit_config.display_rotate.y = 0
        self._area_pb.unit_config.display_rotate.z = 0
        self._area_pb.unit_config.display_translate.x = 0
        self._area_pb.unit_config.display_translate.y = 0
        self._area_pb.unit_config.display_translate.z = 0

        self._area_pb.is_end_no_interpole = False
        self._area_pb.is_start_when_collide_ground = False
        self._area_pb.is_start_when_in_water = False

    def to_proto(self, ctx: SerializerContext):
        self._area_pb.id = ctx.get_next_object_id()
        if self._linkset is not None:
            self._area_pb.links.CopyFrom(self._linkset.to_proto(ctx))
        return self._area_pb


class DeathArea(Area):

    def __init__(self, pos: Vec, scale: Vec):
        super().__init__(obj_name='DeathArea', model_name='AreaCubeTop', pos=pos, scale=scale)

class ChangeStageArea(Area):

    def __init__(self, pos: Vec, scale: Vec, change_stage_id: str, change_stage_name: str, player_start_obj: Object):
        super().__init__(obj_name='ChangeStageArea', model_name='AreaCubeTop', pos=pos, scale=scale)
        self._area_pb.priority = -1
        
        self._area_pb.change_stage_id = change_stage_id
        self._area_pb.change_stage_name = change_stage_name
        self._area_pb.is_only_exit = False
        self._area_pb.is_return_prev_stage = False
        self._area_pb.possessed_actor_type_default_no_check = -2
        self._area_pb.scenario_no = -1
        self._area_pb.shine_got_on_off = 0
        self._area_pb.wipe_type = 'WipeCircle'

        self._linkset = LinkSet(player_restart_pos = [player_start_obj])

class WaterArea(Area):

    def __init__(self, pos: Vec, scale: Vec):
        super().__init__(obj_name='WaterArea', model_name='AreaCubeTop', pos=pos, scale=scale)
        self._area_pb.priority = -1
        
        self._area_pb.is_ice_water = False
        self._area_pb.is_ignore_area = False

class CameraArea(Area):

    def __init__(self, pos: Vec, scale: Vec):
        super().__init__(obj_name='CameraArea', model_name='AreaCubeBase', pos=pos, scale=scale)
        self._area_pb.priority = 200