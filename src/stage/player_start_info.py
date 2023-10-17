from src.stage.proto import stage_pb2
from src.stage.serializer import SerializerContext
from src.math import Vec

class Odyssey:

    def __init__(self, pos: Vec):
        self._pb = stage_pb2.PlayerStartInfo()

        self._pb.is_link_dest = False
        self._pb.unit_config_name = 'ShineTowerRocket'
        self._pb.layer_config_name = 'Common'
        self._pb.placement_file_name = 'WaterfallWorldHomeStage'
        self._pb.is_connect_to_collision = False
        self._pb.material_code = 'Lawn'

        self._pb.rotate.x = 0
        self._pb.rotate.y = 0
        self._pb.rotate.z = 0

        self._pb.scale.x = 1
        self._pb.scale.y = 1
        self._pb.scale.z = 1

        self._pb.translate.x = pos.x()
        self._pb.translate.y = pos.y()
        self._pb.translate.z = pos.z()

        self._pb.unit_config.generate_category = 'PlayerStartInfoList'
        self._pb.unit_config.parameter_config_name = 'ShineTowerRocket'
        self._pb.unit_config.placement_target_file = 'Map'
        self._pb.unit_config.display_scale.x = 1
        self._pb.unit_config.display_scale.y = 1
        self._pb.unit_config.display_scale.z = 1
        self._pb.unit_config.display_rotate.x = 0
        self._pb.unit_config.display_rotate.y = 0
        self._pb.unit_config.display_rotate.z = 0
        self._pb.unit_config.display_translate.x = 0
        self._pb.unit_config.display_translate.y = 0
        self._pb.unit_config.display_translate.z = 0

    def to_proto(self, ctx: SerializerContext):
        self._pb.id = ctx.get_next_object_id()
        return self._pb