from functools import reduce
import math
import struct
import random
from typing import List

from CGAL.CGAL_Kernel import Point_3, Triangle_3, Ray_3, Vector_3, cross_product
from CGAL.CGAL_AABB_tree import AABB_tree_Triangle_3_soup

from src.math import AABB, Vec

import shutil

ENDIAN = '<'

def dot(a: Vector_3, b: Vector_3):
    return a.x()*b.x() + a.y()*b.y() + a.z()*b.z()

class KCL:

    @staticmethod
    def get_collision_data(kcl_file_path: str):
        with open(kcl_file_path, 'rb') as file:
            # Format spec https://mk8.tockdom.com/wiki/KCL_(File_Format)

            ## KCL File Header
            magic_num, = struct.unpack('>I', file.read(4))
            assert magic_num == 0x02020000
            octree_offset, model_offset, model_count = struct.unpack(ENDIAN + 'III', file.read(4*3))
            aabb = AABB(
                minpt=Vec(*struct.unpack(ENDIAN + 'f'*3, file.read(4*3))),
                maxpt=Vec(*struct.unpack(ENDIAN + 'f'*3, file.read(4*3))))
            coordinate_shift = Vec(*struct.unpack(ENDIAN + 'I'*3, file.read(4*3)))

            file.seek(model_offset+4)

            models = []
            for i in range(model_count):
                models.append(KCL.__parse_model(file)) 

            return KCL.CollisionData(models, aabb)
        
    @staticmethod
    def __parse_model(file):
        base_model_offset = file.tell()
        offset_verts, offset_normals, offset_triangles, offset_spatial_index = struct.unpack(ENDIAN + 'i'*4, file.read(4*4))
        file.read(4)
        file.read(12) # spatial grid first coordinate
        coord_mask = Vec(*struct.unpack(ENDIAN + 'I'*3, file.read(4*3)))
        coord_shift = Vec(*struct.unpack(ENDIAN + 'I'*3, file.read(4*3)))
        file.read(4)

        # MODEL_HEADER_SIZE = 0x3C
        # file.seek(base_model_offset + MODEL_HEADER_SIZE)

        file.seek(base_model_offset + offset_verts)
        num_verts = (offset_normals - offset_verts) // 12
        verts = [Point_3(*struct.unpack(ENDIAN + 'f'*3, file.read(4*3))) for _ in range(num_verts)]

        file.seek(base_model_offset + offset_normals)
        num_normals = (offset_triangles - offset_normals) // 12
        normals = [Vector_3(*struct.unpack(ENDIAN + 'f'*3, file.read(4*3))) for _ in range(num_normals)]

        file.seek(base_model_offset + offset_triangles)
        num_tris = (offset_spatial_index - offset_triangles) // 0x14
        triangles = []
        triangle_face_normals = []
        for _ in range(num_tris):
            length, = struct.unpack(ENDIAN + 'f', file.read(4))
            vert_index, = struct.unpack(ENDIAN + 'H', file.read(2))
            dir_index, = struct.unpack(ENDIAN + 'H', file.read(2))
            normal_a_index, normal_b_index, normal_c_index = struct.unpack(ENDIAN + 'HHH', file.read(2*3))
            collision_flags, = struct.unpack(ENDIAN + 'H', file.read(2))
            global_triangle_index, = struct.unpack(ENDIAN + 'I', file.read(4))

            # Conversion code from https://mk8.tockdom.com/wiki/KCL_(File_Format)
            position = verts[vert_index]
            direction = normals[dir_index]
            normal_a = normals[normal_a_index]
            normal_b = normals[normal_b_index]
            normal_c = normals[normal_c_index]
            cross_a  = cross_product(normal_a,direction)
            cross_b  = cross_product(normal_b,direction)
            v1 = position
            v2 = position + cross_b * (length / dot(cross_b,normal_c))
            v3 = position + cross_a * (length / dot(cross_a,normal_c))
            
            triangles.append(Triangle_3(v1, v2, v3))
            triangle_face_normals.append(direction)

        return KCL.Model(verts, triangles, triangle_face_normals)
    

    class Model:

        def __init__(self, verts: List[Vector_3], triangles: List[Triangle_3], triangle_face_normals: List[Vector_3]):
            self.__verts = verts
            self.__triangles = triangles
            self.__triangle_face_normals = triangle_face_normals
            self.__aabb_tree = AABB_tree_Triangle_3_soup(triangles)
            self.__aabb = AABB(
                minpt = reduce(lambda a,b: Vec(min(a.x(), b.x()), min(a.y(), b.y()), min(a.z(), b.z())), [Vec(tri.vertex(i).x(), tri.vertex(i).y(), tri.vertex(i).z()) for tri in triangles for i in range(3)]),
                maxpt = reduce(lambda a,b: Vec(max(a.x(), b.x()), max(a.y(), b.y()), max(a.z(), b.z())), [Vec(tri.vertex(i).x(), tri.vertex(i).y(), tri.vertex(i).z()) for tri in triangles for i in range(3)]),
            )

        def get_aabb(self):
            return self.__aabb

        def intersects(self, sphere_center: Vec, sphere_radius: float):
            point_query = Point_3(sphere_center.x(), sphere_center.y(), sphere_center.z())
            sqd = self.__aabb_tree.squared_distance(point_query)
            # print(f'Distance: {math.sqrt(sqd)}')
            return math.sqrt(sqd) <= sphere_radius

        def try_get_random_standable_pos(self, target_surface_normal: Vec = Vec(0, 1, 0), angle_threshold_degrees: int = 45):
            tri_index = random.randrange(len(self.__triangles))
            tri = self.__triangles[tri_index]
            normal = self.__triangle_face_normals[tri_index]
            # Ensure triangle is roughly flat (e.g. is not a slope/wall, is not on the underside of an object)
            if dot(normal, Vector_3(target_surface_normal.x(), target_surface_normal.y(), target_surface_normal.z())) < math.cos(angle_threshold_degrees * math.pi / 180):
                return None
            pos_on_object_surface = (sum([Vec(tri.vertex(v).x(), tri.vertex(v).y(), tri.vertex(v).z()) for v in range(3)])) / 3
            return pos_on_object_surface, normal
        
        def to_obj(self, vertices: List[Vec], translation: Vec):
            for triangle in self.__triangles:
                for i in range(3):
                    p = triangle.vertex(i)
                    p = Vec(p.x(), p.y(), p.z())
                    vertices.append(p + translation)                
    
    class CollisionData:

        def __init__(self, models, aabb: AABB):
            self.__models: List[KCL.Model] = models
            self.__aabb = aabb
            # self.__aabb = reduce(lambda a,b: a.union(b), [model.get_aabb() for model in models])

        def get_aabb(self):
            return self.__aabb

        def union(self, other_collision_data):
            return KCL.CollisionData(self.__models + other_collision_data.__models, self.__aabb.union(other_collision_data.__aabb))

        def intersects(self, sphere_center: Vec, sphere_radius: float):
            for model in self.__models:
                if model.intersects(sphere_center, sphere_radius):
                    return True
            return False
                    
        def get_random_standable_pos(self, sphere_radius: float, target_surface_normal: Vec = Vec(0, 1, 0), angle_threshold_degrees: int = 45):
            """ Get a pos on this object that is standable for an actor of the given radius. """
            for i in range(10000):
                model = random.choice(self.__models)
                output = model.try_get_random_standable_pos(target_surface_normal, angle_threshold_degrees)
                if output is None:
                    continue
                    
                pos_on_object_surface, normal = output
                actor_center = pos_on_object_surface + Vec(normal.x(), normal.y(), normal.z())*(sphere_radius+1)
                # Ensure the space is large enough for mario to stand
                if self.intersects(actor_center, sphere_radius):
                    continue

                return pos_on_object_surface
            raise Exception('Could not find standable pos on object')
        
        def to_obj(self, vertices: List[Vec], translation: Vec):
            for model in self.__models:
                model.to_obj(vertices, translation)

        