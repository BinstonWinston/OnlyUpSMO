import json
from src.stage.proto import stage_pb2
from src.stage.object import ObjectFactory, LinkSet
from src.stage.serializer import SerializerContext
from src.math import Vec

class ScenarioStartCamera:

    def __init__(self, pos: Vec, rot: Vec):
        self.__linkset = LinkSet(look_at_rail=[LOOK_AT_RAIL],
                                 next_key=[NEXT_KEY],
        # no_delete__shine=[NO_DELETE_SHINE],
                                 switch_alive_keep_on=[STAGE_SWITCH],)
        self.__pb = stage_pb2.ScenarioStartCamera(
            is_keep_pre_self_pose_next_camera = False,
            is_link_dest = False,
            layer_config_name = 'Scenario1',
            model_name = None,
            placement_file_name = 'WaterfallWorldHomeStage',
            play_step = -1,
            unit_config_name = 'ScenarioStartCameraRailMove',
        )
        self.__pb.translate.x = pos.x()
        self.__pb.translate.y = pos.y()
        self.__pb.translate.z = pos.z()
        self.__pb.rotate.x = rot.x()
        self.__pb.rotate.y = rot.y()
        self.__pb.rotate.z = rot.z()
        
        self.__pb.unit_config.generate_category = 'ScenarioStartCameraList'
        self.__pb.unit_config.parameter_config_name = 'ScenarioStartCameraRailMove'
        self.__pb.unit_config.placement_target_file = 'Map'
        self.__pb.unit_config.display_scale.x = 1
        self.__pb.unit_config.display_scale.y = 1
        self.__pb.unit_config.display_scale.z = 1
        self.__pb.unit_config.display_rotate.x = 0
        self.__pb.unit_config.display_rotate.y = 0
        self.__pb.unit_config.display_rotate.z = 0
        self.__pb.unit_config.display_translate.x = 0
        self.__pb.unit_config.display_translate.y = 0
        self.__pb.unit_config.display_translate.z = 0

    def to_proto(self, ctx: SerializerContext):
        self.__pb.id = ctx.get_next_object_id()
        if self.__linkset is not None:
            self.__pb.links.CopyFrom(self.__linkset.to_proto(ctx))
        return self.__pb

LOOK_AT_RAIL = ObjectFactory.create_rail(
    rail_points = [
        Vec(16404.876953125, 1300.0, 4666.904296875),
        Vec(10750.0, 1900.0, -4450.0),
    ],
    rail_type = 'Linear',
)

NEXT_KEY = ObjectFactory.create_next_key(
    look_at_rail = ObjectFactory.create_rail(
        rail_points = [
            Vec(9000, 1800, -2650),
            Vec(6750, 1900, -350),
        ],
        rail_type = 'Bezier',
    )
)

# NO_DELETE_SHINE = ObjectFactory.create_no_delete_shine(

# )

# , 'NoDelete_Shine': [
#         {'CapMessageShowType': 1, 'ChangeStageId': None, 'ChangeStageName': None, 'Color': -1, 'ConnectLength': -1.0, 'FukankunZoomType': 0, 'FukankunZoomWatchTimeThres': 120, 'Id': 'obj214', 'IsAppearDemoHeightHigh': False, 'IsConnectSide': False, 'IsConnectToCollision': False, 'IsFukankunZoomCapMessage': False, 'IsLinkDest': True, 'IsNoRotate': False, 'IsPlayAppearCameraOnlyOnce': False, 'IsUseAppear': True, 'IsUseAppearDemoAfterGet': False, 'IsUseAppearDemoForce': False, 'IsUseEmptyModel': False, 'IsUseGetCamera': False, 'IsUseGetDemoCamera': True, 'IsUseWarpCamera': True, 'IsUseZoom': False, 'IsValidObjectCamera': False, 'LayerConfigName': 'J', 'Links': {'DemoRegister': [
#                     {'CommonId': None, 'DemoName': None, 'Id': 'obj3430', 'IsLinkDest': True, 'LayerConfigName': 'Scenario1', 'Links': {}, 'ModelName': None, 'PlacementFileName': 'WaterfallWorldHomeStage', 'Rotate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                         }, 'Scale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                         }, 'SrcUnitLayerList': [
#                             {'LayerName': 'J', 'LinkName': 'DemoRegister'
#                             },
#                             {'LayerName': 'NoUse', 'LinkName': 'LinkAddDemoRegister'
#                             },
#                             {'LayerName': 'Common', 'LinkName': 'LinkAddDemoRegister'
#                             }
#                         ], 'Translate': {'X': 6068.34130859375, 'Y': 700.0, 'Z': 1237.1580810546875
#                         }, 'UnitConfig': {'DisplayName': 'デモ登録者', 'DisplayRotate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'DisplayScale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                             }, 'DisplayTranslate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'GenerateCategory': 'DemoObjList', 'ParameterConfigName': 'DemoRegister', 'PlacementTargetFile': 'Map'
#                         }, 'UnitConfigName': 'DemoRegister', 'comment': '初ムーンゲット'
#                     }
#                 ], 'PlayerRestartPos': [
#                     {'Id': 'obj1023', 'IsLinkDest': True, 'IsValidEntranceCamera': True, 'LayerConfigName': 'J', 'Links': {}, 'ModelName': None, 'PlacementFileName': 'WaterfallWorldHomeStage', 'Rotate': {'X': 0.0, 'Y': -45.0, 'Z': 0.0
#                         }, 'Scale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                         }, 'SrcUnitLayerList': [
#                             {'LayerName': 'J', 'LinkName': 'PlayerRestartPos'
#                             }
#                         ], 'Translate': {'X': 6120.515625, 'Y': 979.2040405273438, 'Z': 270.515625
#                         }, 'UnitConfig': {'DisplayName': 'プレイヤー開始位置オブジェ【リンク版】', 'DisplayRotate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'DisplayScale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                             }, 'DisplayTranslate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'GenerateCategory': 'CheckPointList', 'ParameterConfigName': 'PlayerStartObj', 'PlacementTargetFile': 'Map'
#                         }, 'UnitConfigName': 'PlayerStartObj', 'comment': None
#                     }
#                 ], 'ShineStand': [
#                     {'Id': 'obj1936', 'IsLinkDest': True, 'LayerConfigName': 'J', 'Links': {'ViewGroup': [
#                                 {'CommonId': None, 'Id': 'obj15', 'IsLinkDest': True, 'LayerConfigName': 'Common', 'Links': {}, 'ModelName': None, 'PlacementFileName': 'WaterfallWorldHomeStage', 'Rotate': {'X': 0.0, 'Y': 45.0, 'Z': 0.0
#                                     }, 'Scale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                                     }, 'SrcUnitLayerList': [
#                                         {'LayerName': 'NoUse', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'Common', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'R', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'P', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'J', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'Scenario1', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'B', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'Scenario1_2', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'G', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'M', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'L', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'C', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'K', 'LinkName': 'ViewGroup'
#                                         },
#                                         {'LayerName': 'T', 'LinkName': 'ViewGroup'
#                                         }
#                                     ], 'Translate': {'X': 1050.0, 'Y': 16000.0, 'Z': -1200.0
#                                     }, 'UnitConfig': {'DisplayName': 'ビューグループ', 'DisplayRotate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                                         }, 'DisplayScale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                                         }, 'DisplayTranslate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                                         }, 'GenerateCategory': 'ObjectList', 'ParameterConfigName': 'GroupView', 'PlacementTargetFile': 'Map'
#                                     }, 'UnitConfigName': 'GroupView', 'comment': None
#                                 }
#                             ]
#                         }, 'ModelName': None, 'PlacementFileName': 'WaterfallWorldHomeStage', 'Rotate': {'X': 0.0, 'Y': 135.0, 'Z': 0.0
#                         }, 'Scale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                         }, 'SrcUnitLayerList': [
#                             {'LayerName': 'J', 'LinkName': 'ShineStand'
#                             }
#                         ], 'Translate': {'X': 5700.0, 'Y': 1000.0, 'Z': 700.0
#                         }, 'UnitConfig': {'DisplayName': 'ムーンの台座', 'DisplayRotate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'DisplayScale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                             }, 'DisplayTranslate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'GenerateCategory': 'ObjectList', 'ParameterConfigName': 'ShineStand', 'PlacementTargetFile': 'Map'
#                         }, 'UnitConfigName': 'ShineStand', 'comment': None
#                     }
#                 ], 'SwitchGetOn': [
#                     {'CommonId': None, 'Id': 'obj215', 'IsLinkDest': True, 'LayerConfigName': 'Scenario1', 'Links': {}, 'ModelName': None, 'PlacementFileName': 'WaterfallWorldHomeStage', 'Rotate': {'X': 0.0, 'Y': 45.0, 'Z': 0.0
#                         }, 'Scale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                         }, 'SrcUnitLayerList': [
#                             {'LayerName': 'J', 'LinkName': 'SwitchGetOn'
#                             },
#                             {'LayerName': 'Scenario1', 'LinkName': 'SwitchAppear'
#                             },
#                             {'LayerName': 'NoUse', 'LinkName': 'SwitchKill'
#                             },
#                             {'LayerName': 'Scenario1', 'LinkName': 'SwitchKill'
#                             }
#                         ], 'Translate': {'X': 4861.5546875, 'Y': 2584.375, 'Z': 1588.4453125
#                         }, 'UnitConfig': {'DisplayName': 'ステージスイッチ', 'DisplayRotate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'DisplayScale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                             }, 'DisplayTranslate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'GenerateCategory': 'ObjectList', 'ParameterConfigName': 'StageSwitch', 'PlacementTargetFile': 'All'
#                         }, 'UnitConfigName': 'StageSwitch', 'comment': None
#                     }
#                 ], 'ViewGroup': [
#                     {'CommonId': None, 'Id': 'obj15', 'IsLinkDest': True, 'LayerConfigName': 'Common', 'Links': {}, 'ModelName': None, 'PlacementFileName': 'WaterfallWorldHomeStage', 'Rotate': {'X': 0.0, 'Y': 45.0, 'Z': 0.0
#                         }, 'Scale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                         }, 'SrcUnitLayerList': [
#                             {'LayerName': 'NoUse', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'Common', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'R', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'P', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'J', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'Scenario1', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'B', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'Scenario1_2', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'G', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'M', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'L', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'C', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'K', 'LinkName': 'ViewGroup'
#                             },
#                             {'LayerName': 'T', 'LinkName': 'ViewGroup'
#                             }
#                         ], 'Translate': {'X': 1050.0, 'Y': 16000.0, 'Z': -1200.0
#                         }, 'UnitConfig': {'DisplayName': 'ビューグループ', 'DisplayRotate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'DisplayScale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                             }, 'DisplayTranslate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                             }, 'GenerateCategory': 'ObjectList', 'ParameterConfigName': 'GroupView', 'PlacementTargetFile': 'Map'
#                         }, 'UnitConfigName': 'GroupView', 'comment': None
#                     }
#                 ]
#             }, 'ModelName': None, 'PlacementFileName': 'WaterfallWorldHomeStage', 'QuestNo': 0, 'Rotate': {'X': 0.0, 'Y': 135.0, 'Z': 0.0
#             }, 'Scale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#             }, 'ScenarioNo': -1, 'ShadowLength': -1.0, 'ShineOptionalId': 'None', 'SrcUnitLayerList': [
#                 {'LayerName': 'Scenario1', 'LinkName': 'NoDelete_Shine'
#                 },
#                 {'LayerName': 'Scenario1', 'LinkName': 'ShineActor'
#                 }
#             ], 'Translate': {'X': 5700.0, 'Y': 1250.0, 'Z': 700.0
#             }, 'UnitConfig': {'DisplayName': 'シャイン', 'DisplayRotate': {'X': 0.0, 'Y': 0.0, 'Z': 0.0
#                 }, 'DisplayScale': {'X': 1.0, 'Y': 1.0, 'Z': 1.0
#                 }, 'DisplayTranslate': {'X': 0.0, 'Y': 75.0, 'Z': 0.0
#                 }, 'GenerateCategory': 'PlayerStartInfoList', 'ParameterConfigName': 'Shine', 'PlacementTargetFile': 'Map'
#             }, 'UnitConfigName': 'Shine', 'comment': None
#         }
# }

STAGE_SWITCH = ObjectFactory.create_stage_switch(pos=Vec(14600, 2050, -1500))
