import byml
import math

class Vec:

    def __init__(self, x, y=None, z=None):
        if isinstance(x, list):
            self._data = x
        else:
            self._data = [x, y, z]

    def x(self):
        return self._data[0]

    def y(self):
        return self._data[1]
    
    def z(self):
        return self._data[2]
    
    def get_data(self):
        return self._data
    
    def to_byml_dict(self):
        return {
            'X': byml.byml.Float(self.x()),
            'Y': byml.byml.Float(self.y()),
            'Z': byml.byml.Float(self.z()),
        }
    
    def rotate_y(self, theta: float):
        return Vec(
            math.cos(theta)*self.x() + math.sin(theta)*self.z(),
            self.y(),
            -math.sin(theta)*self.x() + math.cos(theta)*self.z(),
        )
    
    def distance_to(self, other):
        return (self - other).length()
    
    def length(self):
        return math.sqrt(self.dot(self))
    
    def normalize(self):
        return self / self.length()
    
    def dot(self, other):
        return self.x()*other.x() + self.y()*other.y() + self.z()*other.z()
    
    def __add__(self, x):
        if isinstance(x, Vec):
            return Vec([a+b for a,b in zip(self._data, x._data)])
        elif isinstance(x, int):
            return Vec([a+x for a in self._data])
        elif isinstance(x, float):
            return Vec([a+x for a in self._data])
        else:
            raise ValueError("Unsupported type")
        
    def __radd__(self, other):
        return self + other
    
    def __mul__(self, x):
        if isinstance(x, Vec):
            return Vec([a*b for a,b in zip(self._data, x._data)])
        elif isinstance(x, int):
            return Vec([a*x for a in self._data])
        elif isinstance(x, float):
            return Vec([a*x for a in self._data])
        else:
            raise ValueError("Unsupported type")
        
    def __sub__(self, x):
        if isinstance(x, Vec):
            return Vec([a-b for a,b in zip(self._data, x._data)])
        elif isinstance(x, int):
            return Vec([a-x for a in self._data])
        elif isinstance(x, float):
            return Vec([a-x for a in self._data])
        else:
            raise ValueError("Unsupported type")
    
    def __neg__(self):
        return Vec(0,0,0) - self
        
    def __truediv__(self, x):
        if isinstance(x, Vec):
            return Vec([a/b for a,b in zip(self._data, x._data)])
        elif isinstance(x, int):
            return Vec([a/x for a in self._data])
        elif isinstance(x, float):
            return Vec([a/x for a in self._data])
        else:
            raise ValueError("Unsupported type")

