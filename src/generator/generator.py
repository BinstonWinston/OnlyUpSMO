from functools import reduce
import math
import random
from typing import List
from src.generator.data.kingdom_dataset import KingdomDataset
from src.generator.data.jump_dataset import JumpDataset, JumpData
from src import stage
from src.math import Vec
from src.config import GlobalConfig

class Trajectory:

    def __init__(self, points: List[Vec]):
        self.__points = points
        if self.__points[0] != Vec(0,0,0):
            # Translate so jump trajectory starts at the origin
            self.__points = [p - self.__points[0] for p in self.__points]

    def endpoint(self):
        return self.__points[-1]
    
    def scale(self, scale: float):
        return Trajectory([p*scale for p in self.__points])
    
    def intersects_object(self, start_pos: Vec, y_rotation: float, radius: float, obj: stage.Object):
        for point in self.__points:
            p = start_pos + point.rotate_y(y_rotation)
            if obj.test_collision(p, radius):
                return True
        return False
    
    def points(self):
        return self.__points

MARIO_RADIUS = 180
CAPPY_RADIUS = 90

class Jump:

    def __init__(self, obj1: stage.Object, obj2: stage.Object, jump_start_pos: Vec, y_rotation: float, mario_trajectory: Trajectory, cappy_trajectory: Trajectory):
        self.__mario_trajectory = mario_trajectory
        self.__cappy_trajectory = cappy_trajectory
        self.__obj1 = obj1
        self.__obj2 = obj2
        self.__y_rotation = y_rotation
        self.__jump_start_pos = jump_start_pos

    def is_possible(self, objs: List[stage.Object], jumps):
        # check this jump doesn't intersect any objects in the list
        for obj in objs:
            if self.intersects_object(obj[0]):
                print(f"Intersected with on: {obj[0].name()}")
                return False
            
        # check new object (self.__obj2) doesn't intersect and of the existing jumps
        new_obj = self.__obj2
        for jump in jumps:
            if jump.intersects_object(new_obj):
                return False
        
        return True

    def intersects_object(self, obj: stage.Object):
        return self.__mario_trajectory.intersects_object(self.__jump_start_pos + Vec(0, stage.Object.Y_OFFSET, 0), self.__y_rotation, MARIO_RADIUS, obj) and \
               self.__cappy_trajectory.intersects_object(self.__jump_start_pos + Vec(0, stage.Object.Y_OFFSET, 0), self.__y_rotation, CAPPY_RADIUS, obj)


    def add_debug_viz(self, scenario: stage.Scenario):
        pass
        # for p in self.__mario_trajectory.points()[::5]:
        #     scenario.add_object(stage.ObjectFactory.create_debug_viz('DebugVizSphere', 
        #                                                              p.rotate_y(self.__y_rotation) + self.__jump_start_pos, scale=Vec(MARIO_RADIUS, MARIO_RADIUS, MARIO_RADIUS),
        #                                                              debug_links=[self.__obj1, self.__obj2]))


class SegmentBase:

    def __init__(self, num_objects: int, kingdom_dataset: KingdomDataset):
        self.__num_objs_remaining = num_objects
        self._kingdom_dataset = kingdom_dataset

    def decrement_num_objs_remaining(self):
        self.__num_objs_remaining -= 1

    def increment_num_objs_remaining(self):
        self.__num_objs_remaining += 1

    def is_last_obj_in_segment(self):
        return self.__num_objs_remaining == 1
        
    def is_done(self):
        return self.__num_objs_remaining <= 0
        
    def get_random_object_name(self):
        return random.choice(self.object_set())
        
    def get_random_jump(self):
        return random.choice(self.jump_set())    
    def get_jump_scale(self, jump_name):
        if random.random() < 1/5:
            return random.uniform(0.8, 1.1)
        else:
            return random.uniform(0.4, 0.9)
        
    def get_random_jump_y_rotation(self):
        return random.uniform(0, 2*math.pi)
        
    def get_entry_pos_on_obj_surface(self, obj_name: str, collision):
        return self.__get_standable_pos_on_obj_surface(collision), Vec(0, 1, 0)

    def get_exit_pos_on_obj_surface(self, obj_name: str, collision):
        return self.__get_standable_pos_on_obj_surface(collision)

    def __get_standable_pos_on_obj_surface(self, collision):
        # Returns pos on obj surface in local obj space (relative to obj origin)
        return collision.get_random_standable_pos(MARIO_RADIUS)

    def object_set(self):
        pass

    def jump_set(self):
        pass

    def create_object(self, obj_name: str, pos: Vec):
        pass

    def initial_objects(self, segment_start_pos: Vec):
        pass


class DefaultSegment(SegmentBase):

    def __init__(self, kingdom_dataset: KingdomDataset, allow_moving_objects: bool):
        super().__init__(num_objects=random.randint(7, 11), kingdom_dataset=kingdom_dataset)
        self.__allow_moving_objects = allow_moving_objects

    def object_set(self):
        return self._kingdom_dataset.get_objects()
    
    def jump_set(self):
        return JumpDataset.get_all_jumps(capture_type=None)
    
    def create_object(self, obj_name: str, pos: Vec, is_last_obj: bool, prev_obj: stage.Object, jump_offset: Vec):
        if self.__allow_moving_objects and (not is_last_obj) and random.uniform(0,1) < 0.4 and (prev_obj.get_parameter_config_name() != 'KeyMoveMapParts') and \
              (stage.ObjectFactory.get_collision(obj_name).get_aabb().max_dim() < 1000):
            points = [
                pos,
                pos + Vec(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))*500 - jump_offset.normalize()*750,
            ]
            speed = random.uniform(7, 15)
            obj = stage.ObjectFactory.create_key_move_parts(obj_name,
                stage.Components.KeyMoveNext.Key(points[0], speed, 0), 
                stage.Components.KeyMoveNext.Key(points[1], speed, 0),
            )
            obj.set_comment('DefaultSegment')
            rail = stage.ObjectFactory.create_rail(points)
            rail_drawer = stage.Object('RailDrawer', 'RailDrawer', pos=pos, linkset=stage.LinkSet(rail=[rail]))
            return [obj, rail_drawer]
        else:
            obj = stage.ObjectFactory.create_fix_map_parts(obj_name, pos=pos)
            obj.set_comment('DefaultSegment')
            return [obj]

    
    def initial_objects(self, segment_start_pos: Vec):
        return []
    
class TimerSegment(SegmentBase):

    def __init__(self, cappyless: bool, segment_type, kingdom_dataset: KingdomDataset):
        super().__init__(num_objects=random.randint(4, 6), kingdom_dataset=kingdom_dataset)
        self.__cappyless = cappyless
        self.__segment: SegmentBase = segment_type(kingdom_dataset=kingdom_dataset, allow_moving_objects=True)
        self.__timer_start_obj = None

    def object_set(self):
        return self.__segment.object_set()
    
    def jump_set(self):
        return self.__segment.jump_set()
    
    def increment_num_objs_remaining(self):
        super().increment_num_objs_remaining()
        # Revert linking so reverted object isn't accidentally included in the stage
        self.__timer_start_obj.linkset().switch_appear_target[:] = self.__timer_start_obj.linkset().switch_appear_target[:-1]
    
    def create_object(self, obj_name: str, pos: Vec, is_last_obj: bool, prev_obj: stage.Object, jump_offset: Vec):
        objs = self.__segment.create_object(obj_name=obj_name,
                                           pos=pos,
                                           is_last_obj=is_last_obj,
                                           prev_obj=prev_obj,
                                           jump_offset=jump_offset)
        for obj in objs:
            obj.set_is_link_dest(True)
            obj.set_comment('TimerSegment')
            self.__timer_start_obj.linkset().switch_appear_target.append(obj)
            # obj.linkset().group_clipping = [self.__group_clipping]
        return objs
    
    def initial_objects(self, segment_start_pos: Vec):
        self.__timer_start_obj = stage.ObjectFactory.create_trample_switch_timer(
            pos=segment_start_pos - Vec(0, 200, 0),
            duration_in_frames = 30 * 60, # TODO update this based on number of jumps
        )
        self.__timer_start_obj.linkset().switch_appear_target = [] # Required, if this is not added, appending to the links will append to the shared default constructor array and be applied to all objects causes a bunch of issues
        # self.__group_clipping = stage.Object('GroupClipping', 'GroupClipping', pos=segment_start_pos, is_link_dest=True)
        # stage_switch = stage.ObjectFactory.create_stage_switch()
        # self.__timer_start_obj.linkset().camera_switch_on = [stage_switch]
        # camera_area = stage.Area(obj_name='CameraArea', model_name='AreaCubeBase', pos=segment_start_pos, scale=Vec(5000,5000,5000), linkset=stage.LinkSet(switch_appear=[stage_switch]))
        return [self.__timer_start_obj] + self.__segment.initial_objects(segment_start_pos)
    
class MoeEyeSegment(SegmentBase):

    def __init__(self):
        super().__init__(num_objects=random.randint(5, 6), kingdom_dataset=None)

    def object_set(self):
        return ['SandWorldHomeMeganeStep001', 'SandWorldHomeMeganeStep000']
    
    def jump_set(self):
        return JumpDataset.get_all_jumps()
    
    def get_jump_scale(self, jump_name):
        return random.uniform(0.3, 0.4)
    
    def create_object(self, obj_name: str, pos: Vec, is_last_obj: bool, prev_obj: stage.Object, jump_offset: Vec):
        if self.is_last_obj_in_segment():
            return [stage.ObjectFactory.create_fix_map_parts('SandWorldHomeLift001', pos=pos)]
        else:
            return [stage.Object(obj_name, parameter_config_name='MeganeMapParts', pos=pos)]
    
    def initial_objects(self, segment_start_pos: Vec):
        pos = segment_start_pos + Vec(500, 0, 0)
        capture = stage.Object('Megane', parameter_config_name='Megane', pos=pos + Vec(0, 50, 0))
        # to prevent it from escaping or falling
        capture_platforms = [
            stage.ObjectFactory.create_fix_map_parts('SandWorldHomeLift000', pos=pos),
            stage.ObjectFactory.create_fix_map_parts('SandWorldHomeLift000', pos=pos + Vec(0, 0, -150), rot=Vec(90, 0, 0)),
            stage.ObjectFactory.create_fix_map_parts('SandWorldHomeLift000', pos=pos + Vec(0, 0, 150), rot=Vec(-90, 0, 0)),
            stage.ObjectFactory.create_fix_map_parts('SandWorldHomeLift000', pos=pos + Vec(150, 0, 0), rot=Vec(0, 0, 90)),
            stage.ObjectFactory.create_fix_map_parts('SandWorldHomeLift000', pos=pos + Vec(-150, 0, 0), rot=Vec(0, 0, -90)),
        ]
        return capture_platforms + [capture]
    


class LavaBubbleSegment(SegmentBase):

    def __init__(self):
        super().__init__(num_objects=random.randint(7, 9), kingdom_dataset=None)

    def object_set(self):
        return ['LavaWorldBubbleLaneExKeyMoveParts000']
    
    def jump_set(self):
        return JumpDataset.get_all_jumps('TestCaptureBubble')
    
    def get_jump_scale(self, jump_name):
        return random.uniform(0.8, 1)
    
    def create_object(self, obj_name: str, pos: Vec, is_last_obj: bool, prev_obj: stage.Object, jump_offset: Vec):
        if self.is_last_obj_in_segment():
            return [stage.ObjectFactory.create_fix_map_parts('LavaWorldHomeTimer002WobbleParts000', pos=pos)]
        else:
            if random.random() < 0.5:
                points = [
                    pos,
                    pos + Vec(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))*150
                ]
                speed = random.uniform(3, 6)
                obj = stage.ObjectFactory.create_key_move_parts(obj_name,
                    stage.Components.KeyMoveNext.Key(points[0], speed, 0), 
                    stage.Components.KeyMoveNext.Key(points[1], speed, 0),
                )
                rail = stage.ObjectFactory.create_rail(points)
                rail_drawer = stage.Object('RailDrawer', 'RailDrawer', pos=pos, linkset=stage.LinkSet(rail=[rail]))
                return [obj, rail_drawer]
            else:
                return [stage.ObjectFactory.create_fix_map_parts(obj_name, pos=pos)]
    
    def initial_objects(self, segment_start_pos: Vec):
        pos = segment_start_pos + Vec(250, 0, 0)
        capture = stage.ObjectFactory.create_move_next('TestCaptureBubble', parameter_config_name='Bubble', 
                               key1=stage.Components.MoveNext.Key(pos + Vec(0, 300, 0), 0, 10, 0), 
                               key2=stage.Components.MoveNext.Key(pos + Vec(0, 0, 0), 120, 10, 60))
        initial_lava = stage.ObjectFactory.create_fix_map_parts('LavaWorldBubbleLaneExKeyMoveParts000', pos=pos + Vec(0, -350, 0))
        return [capture, initial_lava]
    
class PokioSegment(SegmentBase):

    def __init__(self):
        super().__init__(num_objects=random.randint(3, 4), kingdom_dataset=None)

    def object_set(self):
        return ['SkyWorldHomeRotateParts000', 'SkyWorldHomeConveyerParts001']
    
    def jump_set(self):
        return JumpDataset.get_all_jumps('Pokio')
    
    def get_jump_scale(self, jump_name):
        return random.uniform(0.8, 1)
    
    def get_random_jump_y_rotation(self):
        return 0

    def get_entry_pos_on_obj_surface(self, obj_name: str, collision):
        if obj_name not in self.object_set(): # finding entry pos of final object in this segment that is a normal non-pokio platform
            return super().get_entry_pos_on_obj_surface(obj_name, collision)
        pos = reduce(lambda a,b: a if a.y() < b.y() else b, self.__get_random_pokeable_positions(collision))
        # print(f'Entry: {pos.to_byml_dict()}')
        return pos, Vec(0, 0, 0)

    def get_exit_pos_on_obj_surface(self, obj_name: str, collision):
        if obj_name not in self.object_set(): # finding exit pos of previous segment's last object. In this case, use normal generation from the surface of the object
            return super().get_exit_pos_on_obj_surface(obj_name, collision)
        pos = reduce(lambda a,b: a if a.y() > b.y() else b, self.__get_random_pokeable_positions(collision))
        # print(f'Exit: {pos.to_byml_dict()}')
        return pos

    def __get_random_pokeable_positions(self, collision):
        SAMPLE_COUNT = 20
        return [
            collision.get_random_standable_pos(MARIO_RADIUS, target_surface_normal=Vec(0, 0, 1), angle_threshold_degrees=45)
            for _ in range(SAMPLE_COUNT)
        ]
    
    def create_object(self, obj_name: str, pos: Vec, is_last_obj: bool, prev_obj: stage.Object, jump_offset: Vec):
        if self.is_last_obj_in_segment():
            return [stage.ObjectFactory.create_fix_map_parts('LavaWorldHomeTimer002WobbleParts000', pos=pos + Vec(0, -1750, -500))]
        else:
            points = [
                pos + Vec(0, 0, 0),
                pos + Vec(random.uniform(250, 700), 0, 0)
            ]
            speed = random.uniform(3, 6)
            obj = stage.ObjectFactory.create_key_move_parts(obj_name,
                stage.Components.KeyMoveNext.Key(points[0], speed, 0), 
                stage.Components.KeyMoveNext.Key(points[1], speed, 0),
            )
            return [obj]
    
    def initial_objects(self, segment_start_pos: Vec):
        capture = stage.Object('Tsukkun', parameter_config_name='Tsukkun', pos=segment_start_pos + Vec(0, 150, 0), components=[stage.Components.Capture(cap_name='EnemyCapTsukkun')])
        starting_wall = stage.ObjectFactory.create_fix_map_parts('SkyWorldHomeRotateParts000', pos=segment_start_pos + Vec(0, 0, -250))
        # platform to prevent pokio from escaping or falling
        capture_platform = stage.ObjectFactory.create_fix_map_parts('SeaWorldHomeSwitchKeyMoveParts000', pos=segment_start_pos)
        return [capture_platform, capture, starting_wall]


class Zone:

    def __init__(self, name: str, base_pos: Vec = Vec(0,0,0)):
        self.name = name
        self.base_pos = base_pos
        self.scenario = stage.Scenario(default_data=False)
class Generator:

    def __init__(self, kingdom_dataset: KingdomDataset): #, difficulty)
        self.__dataset = kingdom_dataset

    def generate(self, player_start_pos: Vec, current_stage_name: str, prev_stage_name: str, next_stage_name: str):
        starting_platform_obj_name = 'CapWorldHomeGround001' if self.__dataset.name() != 'LavaWorld' else 'LavaWorldHomeTimer002WobbleParts000' # CapWorldHomeGround001 causes tons of lag in LavaWorld (maybe grass + heat distortion is laggy, idk)
        objs = [[stage.ObjectFactory.create_fix_map_parts(starting_platform_obj_name, pos=player_start_pos - Vec(0, 1500, 0))]]
        jumps = []
        collision_debug_verts = []
        num_objects = 55 if self.__dataset.name() != 'SkyWorld' else 45

        SEGMENT_CREATORS = [
            lambda d: DefaultSegment(d, allow_moving_objects=True),
        ]

        if self.__dataset.name() not in ['WaterfallWorld', 'SeaWorld']: # these have some object that causes a crash on timer challenges (I think due to clipping or something)
            SEGMENT_CREATORS.append(lambda d: TimerSegment(cappyless=random.choice([False, True]), 
                                                           segment_type=DefaultSegment, 
                                                           kingdom_dataset=d))

        if self.__dataset.name() in ['SandWorld']:
            SEGMENT_CREATORS.append(lambda d: MoeEyeSegment())
        if self.__dataset.name() in ['LavaWorld']:
            SEGMENT_CREATORS.append(lambda d: LavaBubbleSegment())
        elif self.__dataset.name() in ['SkyWorld']:
            SEGMENT_CREATORS.append(lambda d: PokioSegment())

        def add_initial_objects(segment: SegmentBase):
            for obj in segment.initial_objects(objs[-1][0].pos() + segment.get_exit_pos_on_obj_surface(objs[-1][0].name(), objs[-1][0].get_collision())):
                if isinstance(obj, stage.Area):
                    zones[-1].scenario.add_area(obj)
                elif isinstance(obj, stage.Object):
                    if obj.get_collision() is not None:
                        objs.append([obj])
                    zones[-1].scenario.add_object(obj)
                else:
                    raise Exception(f'Unsupported initial object: {obj}')

        segment: SegmentBase = random.choice(SEGMENT_CREATORS)(self.__dataset)

        zones = [Zone(f'OnlyUp{self.__dataset.name()}{type(segment).__name__}Zone0')]
        zone_obj_indices = []
        zone_jump_indices = []

        add_initial_objects(segment)

        while len(objs) < num_objects:
            if segment.is_done():
                prev_segment = segment
                if len(SEGMENT_CREATORS) == 1:
                    segment = SEGMENT_CREATORS[0](self.__dataset)
                else:
                    while type(segment).__name__ == type(prev_segment).__name__: # Ensure the same segment type doesn't occur back-to-back unless there is only one type
                        segment = random.choice(SEGMENT_CREATORS)(self.__dataset)
                zones.append(Zone(f'OnlyUp{self.__dataset.name()}{type(segment).__name__}Zone{len(zones)}'))
                zone_obj_indices.append(len(objs))
                zone_jump_indices.append(len(jumps))
                add_initial_objects(segment)
            jump_data = self.__find_new_jump(objs, jumps, collision_debug_verts, segment=segment, is_last_obj=len(objs)==num_objects-1, player_start_pos=player_start_pos, zone_obj_indices=zone_obj_indices, zone_jump_indices=zone_jump_indices, target_num_objs=num_objects)
            if jump_data is None:
                continue
            new_obj, new_jump = jump_data
            objs.append(new_obj)
            jumps.append(new_jump)
            segment.decrement_num_objs_remaining()
        zone_obj_indices.append(len(objs))
        
        zone_index = 0
        for i in range(len(objs)):
            if i >= zone_obj_indices[zone_index]:
                zone_index += 1
            for obj in objs[i]:
                if not obj.is_link_dest():
                    zones[zone_index].scenario.add_object(obj)

        for jump in jumps:
            jump.add_debug_viz(zones[0].scenario)

        if GlobalConfig.args.object_collision_debug_dir:
            with open(os.path.join(GlobalConfig.args.object_collision_debug_dir, f'collision-debug-{self.__dataset.name()}.obj', 'w+')) as obj_file:
                for v in collision_debug_verts:
                    v -= player_start_pos
                    obj_file.write(f'v {v.x()} {v.y()} {v.z()}\n')
                for i in range(0, len(collision_debug_verts), 3):
                    obj_file.write(f'f {i+1} {i+2} {i+3}\n')

        main_scenario = stage.Scenario(sky_name=self.__dataset.get_sky_name())
        for zone in zones:
            main_scenario.add_zone(zone)

        if self.__dataset.name() == 'SeaWorld':
            vball_pos = objs[-1][0].pos() + Vec(1600, 1000, 0)
            for x in range(-1, 2):
                for y in range(-1, 2):
                    main_scenario.add_object(stage.ObjectFactory.create_fix_map_parts('SandWorldHomeLift001', pos=vball_pos + Vec(x*800, 0, y*800)))
            beach_vball_zone = Zone('SeaWorldBeachVolleyBallZone', vball_pos)
            beach_vball_zone.scenario = None # Remove scenario data since it's an existing zone and nothing new needs to be written
            main_scenario.add_zone(beach_vball_zone)
            main_scenario.add_object(stage.ObjectFactory.create_stage_change_pipe(next_stage_name, vball_pos + Vec(0, 0, -800)))
        else:
            main_scenario.add_object(stage.ObjectFactory.create_stage_change_pipe(next_stage_name, objs[-1][0].pos() + Vec(0, 450, 0)))


        height_of_last_object = objs[-1][0].pos().y()
        if self.__dataset.name() == 'SeaWorld':
            height_of_last_object += 2500 # for beach vball zone
        self.__add_warp_areas_between_stages(main_scenario, height_of_last_object, player_start_pos, 
                                             current_stage_name=current_stage_name,
                                             prev_stage_name=prev_stage_name, 
                                             next_stage_name=next_stage_name)
        
        main_scenario.add_object(stage.Object('LifeMaxUpItem', parameter_config_name='LifeMaxUpItem', pos=player_start_pos + Vec(250, -800, 0)))

        return main_scenario

    def __find_new_jump(self, objs: List[stage.Object], jumps: List[Jump], collision_debug_verts: List[Vec], segment: SegmentBase, is_last_obj: bool, player_start_pos: Vec, zone_obj_indices: List[int], zone_jump_indices: List[int], target_num_objs: int):
        def add_object_collision_debug(obj: stage.Object):
            obj.get_collision().to_obj(collision_debug_verts, obj.pos())

        new_obj = None
        for i in range(100):
            
            new_obj_name = segment.get_random_object_name() if not is_last_obj else 'LavaWorldWireStep000' # Force lava world wire step as final platform
            # print(f'Trying: {new_obj_name}')

            jump_type = segment.get_random_jump()

            random_rotation = segment.get_random_jump_y_rotation()
            jump_scale = segment.get_jump_scale(jump_type.name())

            mario_trajectory = Trajectory(jump_type.get_mario_trajectory()).scale(jump_scale)
            cappy_trajectory = Trajectory(jump_type.get_mario_trajectory()).scale(jump_scale)

            jump_offset = mario_trajectory.endpoint().rotate_y(random_rotation)
            jump_start_pos = objs[-1][0].pos() + (segment.get_exit_pos_on_obj_surface(objs[-1][0].name(), objs[-1][0].get_collision())) # Must ADD the local surface pos offset because we already have the obj pos and are offsetting the next jump. You only need to subtract the local offset when trying to place the destination object so the jump lands at the target local standing pos offset.
            local_object_jump_landing_pos, entry_normal = segment.get_entry_pos_on_obj_surface(new_obj_name, stage.ObjectFactory.get_collision(new_obj_name))
            new_obj_pos = jump_start_pos + jump_offset - local_object_jump_landing_pos - entry_normal*(MARIO_RADIUS+1)

            if random.random() < new_obj_pos.distance_to(player_start_pos) / 35_000: # If an object is this distance away, then there is a 100% chance it will get cut and retried. If it's half this distance, then 50% chance, etc.
                # This guides the stage vertically upwards and prevents it from drifting too far away from the start
                # This makes falls less likely to cause a total reset to the begininning
                # Russian roulette style termination of jumps based on distance from player start pos in XZ plane
                continue
        
            # print(f'Trying: {new_obj_name}')
            # print(new_obj_pos.to_byml_dict())
            new_objs = segment.create_object(new_obj_name, 
                                            pos=new_obj_pos, 
                                            is_last_obj=is_last_obj,
                                            prev_obj=objs[-1][0],
                                            jump_offset=jump_offset)
            new_obj = new_objs[0]
            new_jump = Jump(objs[-1][0], new_obj, jump_start_pos=jump_start_pos, y_rotation=random_rotation, mario_trajectory=mario_trajectory, cappy_trajectory=cappy_trajectory)
            if new_jump.is_possible(objs, jumps):
                add_object_collision_debug(new_obj)
                print(f'[{len(objs)}/{target_num_objs}] Added: {new_obj_name}')
                return new_objs, new_jump
        if len(objs) > zone_obj_indices[-1] and len(jumps) > zone_jump_indices[-1]: # Make sure we don't revert across zone boundaries and potentially cause an impossible section or leftover links
            print(f'Failed on {objs[-1][0].name()}, reverting slightly and re-attempting')
            objs[:] = objs[:-1]
            jumps[:] = jumps[:-1]
            segment.increment_num_objs_remaining()
        else:
            # revert entire previous segment
            objs[:] = objs[:zone_obj_indices[-1]]
            jumps[:] = jumps[:zone_jump_indices[-1]]
            zone_obj_indices[:] = zone_obj_indices[:-1]
            zone_jump_indices[:] = zone_jump_indices[:-1]
            print(f'Failed, reverting entire previous segment')
        return None
        # raise Exception(f'Max number of new jump tries exceeded, exiting to prevent infinite loop. Stuck on object {objs[-1][0].name()}')        

    def __add_warp_areas_between_stages(self, main_scenario: stage.Scenario, end_of_stage_height: float, player_start_pos: Vec, current_stage_name: str, prev_stage_name: str, next_stage_name: str):
        # Add captures below in case captures die and need to respawn
        main_scenario.add_area(stage.DeathArea(
            player_start_pos + Vec(0, -4000, 0),
            Vec(100000, 20, 100000),
        ))
        
        
        AREA_SIZE = 4000
        NUM_AREAS_PER_SIDE = 8
        
        # Top of the stage, the entry points when falling down from the next stage
        for x in range(NUM_AREAS_PER_SIDE):
            for y in range(NUM_AREAS_PER_SIDE):
                fall_warp_spawn_point = Vec(player_start_pos.x(), end_of_stage_height + 2000, player_start_pos.z()) + Vec((x-NUM_AREAS_PER_SIDE/2)*AREA_SIZE, 0, (y-NUM_AREAS_PER_SIDE/2)*AREA_SIZE)
                fall_warp_spawn_obj = stage.Object('PlayerStartObj', 'PlayerStartObj', pos=fall_warp_spawn_point)
                main_scenario.add_object(fall_warp_spawn_obj)
                main_scenario.add_area(stage.ChangeStageArea(
                    fall_warp_spawn_point + Vec(0, 20000, 0),
                    Vec(0.001, 0.001, 0.001),
                    change_stage_name=next_stage_name,
                    change_stage_id=f'EX_FallFromTop_{x}_{y}',
                    player_start_obj=fall_warp_spawn_obj,
                ))
                main_scenario.add_area(stage.WaterArea( # Mario will touch this briefly while falling and will restore control to the player, so they can try to save the fall
                    fall_warp_spawn_point + Vec(0, -500, 0),
                    Vec(0.25, 0.25, 0.25),
                ))


        if prev_stage_name is None:
            # If it's the first kingdom, warp area to player starting pos on same stage
            # This needs to be a warp area, not a death area, because if it's a death area you'll respawn in the playerstartobj of the stage, and if you fell down from the top, that means you'll respawn at the top of the starting stage instead of the initial platform
            fall_warp_spawn_point = player_start_pos
            fall_warp_spawn_obj = stage.Object('PlayerStartObj', 'PlayerStartObj', pos=fall_warp_spawn_point)
            main_scenario.add_object(fall_warp_spawn_obj)
            main_scenario.add_area(stage.ChangeStageArea(
                fall_warp_spawn_point + Vec(0, -2000, 0),
                Vec(100000, 20, 100000),
                change_stage_name=current_stage_name,
                change_stage_id=f'EX_FallFromTop_InitialStage',
                player_start_obj=fall_warp_spawn_obj,
            ))
        else:
            # Huge warp default warp area to cover the whole thing as a backup if players fall thru the random areas
            spawn_pos = Vec(player_start_pos.x(), end_of_stage_height + 2000, player_start_pos.z())
            spawn_obj = stage.Object('PlayerStartObj', 'PlayerStartObj', pos=player_start_pos, components=[stage.Components.StageChange('')])
            main_scenario.add_area(stage.ChangeStageArea(
                        spawn_pos + Vec(0, 20000, 0),
                        Vec(0.001, 0.001, 0.001),
                        change_stage_name=next_stage_name,
                        change_stage_id=f'EX_FallFromTop_Default',
                        player_start_obj=spawn_obj,
                    ))
            main_scenario.add_area(stage.ChangeStageArea(
                                    player_start_pos + Vec(0, -3000, 0),
                                    Vec(100000, 20, 100000),
                                    change_stage_name=prev_stage_name,
                                    change_stage_id='EX_FallFromTop_Default',
                                    player_start_obj=spawn_obj
                                ))
        
            for x in range(NUM_AREAS_PER_SIDE):
                for y in range(NUM_AREAS_PER_SIDE):
                    main_scenario.add_area(stage.ChangeStageArea(
                                    player_start_pos + Vec((x-NUM_AREAS_PER_SIDE/2)*AREA_SIZE, -2000, (y-NUM_AREAS_PER_SIDE/2)*AREA_SIZE),
                                    Vec(AREA_SIZE/1000, AREA_SIZE/1000, AREA_SIZE/1000),
                                    change_stage_name=prev_stage_name,
                                    change_stage_id=f'EX_FallFromTop_{x}_{y}',
                                    player_start_obj=spawn_obj
                                ))