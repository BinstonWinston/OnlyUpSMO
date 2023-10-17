from src.math import Vec

class AABB:
    def __init__(self, minpt, maxpt):
        self.minpt = minpt
        self.maxpt = maxpt

    def union(self, other):
        return AABB(
            Vec(min(self.minpt.x(), other.minpt.x()), min(self.minpt.y(), other.minpt.y()), min(self.minpt.z(), other.minpt.z())),
            Vec(max(self.maxpt.x(), other.maxpt.x()), max(self.maxpt.y(), other.maxpt.y()), max(self.maxpt.z(), other.maxpt.z()))
        )
    
    def to_dict(self):
        return {
            'min': self.minpt._data,
            'max': self.maxpt._data,
        }
    
    def translate(self, p: Vec):
        return AABB(
            minpt = self.minpt + p,
            maxpt = self.maxpt + p,
        )
    
    def scale(self, s):
        center = Vec(0.5,0.5,0.5) * (self.maxpt + self.minpt)
        minpt = (Vec(s,s,s) * (self.minpt - center)) + center
        maxpt = (Vec(s,s,s) * (self.maxpt - center)) + center
        return AABB(minpt, maxpt)
    
    def max_dim(self):
        return max(self.maxpt.x() - self.minpt.x(), max(self.maxpt.y() - self.minpt.y(), self.maxpt.z() - self.minpt.z()))
    
    def intersects(self, sphere_center: Vec, sphere_radius: Vec):
        dmin = 0
        for i in range(3):
            if (sphere_center.get_data()[i] < self.minpt.get_data()[i]):
                dmin += (sphere_center.get_data()[i] - self.minpt.get_data()[i])**2
            if (sphere_center.get_data()[i] > self.maxpt.get_data()[i]):
                dmin += (sphere_center.get_data()[i] - self.maxpt.get_data()[i])**2

        if dmin <= sphere_radius:
            print(dmin, sphere_center.to_byml_dict(), sphere_radius, self.minpt.to_byml_dict(), self.maxpt.to_byml_dict())

        return dmin <= sphere_radius