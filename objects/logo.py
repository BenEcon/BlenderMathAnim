import numpy as np

from objects.bobject import BObject
from objects.circle import Circle, Circle2
from objects.coordinate_system import CoordinateSystem
from utils.constants import DEFAULT_ANIMATION_TIME

def logo_curve(t=0,n=20):
    """draws the logo when the parameter runs from -pi to pi"""
    t = n*t
    lined_circles = 0.25*(-1)**np.floor(np.abs(t)/np.pi)*np.cos((-1)**np.floor(np.abs(t)/np.pi)*np.abs(t))-0.5*np.floor(np.abs(t)/np.pi)+n/4+1j*(1/4*np.sin(t)+3/4)
    return 1/np.conj(lined_circles)

class Logo(CoordinateSystem):
    """
    """

    def __init__(self, location=[0, 0, 0],
                 details=10, length=1, colors=['important', 'example', 'drawing'], thickness=0.1, **kwargs):
        """

        example:

        logo = Logo(location=[7, 0, 0], length=10, colors=['important', 'drawing', 'drawing'],thickness=0.1,details=100)
        logo.appear(begin_times=prime_occurance_times, transition_times=[1])


        :param location:
        :param detail:
        :param length:
        :param colors:
        :param thickness:
        :param kwargs:
        """

        super().__init__(dim=2, lengths=[length, length], radii=[0.03, 0.03], domains=[[-1, 1], [0, 2]],
                         all_n_tics=[2, 2], location_of_origin=location, labels=["x", "y"],
                         all_tic_labels=[np.arange(-1, 1.1, 1), np.arange(-0, 2, 1)],
                         materials=['drawing', 'drawing'], name='coordinate_system_for_logo',
                         text_size='large', **kwargs)

        self.begin_times = None
        self.red_circles = []
        self.blue_circles = []
        self.green_circles = []

        for i in range(0, details + 1):
            den = 2 + i * i
            r = 1 / den
            x = 2 * i / den
            y = 3 / den
            self.red_circles.append(Circle(self, center=[x, y, 0], radius=r, thickness=thickness*np.sqrt(2*r), color=colors[0],
                                           name='red_circle_' + str(i)))

            if i > 0:
                den = 2 + i * i
                r = 1 / den
                x = -2 * i / den
                y = 3 / den
                self.red_circles.append(Circle(self, center=[x, y, 0], radius=r, thickness=thickness*np.sqrt(2*r), color=colors[0],
                                               name='red_circle_' + str(i)))

        for i in range(1, details + 1):
            den = 6 + 4 * i * (i - 1)
            r = 1 / den
            x = (8 * i - 4) / den
            y = 9 / den
            self.green_circles.append(Circle(self, center=[x, y, 0], radius=r, thickness=thickness*np.sqrt(6*r), color=colors[1],
                                             name='green_circle_' + str(i)))

            j = i - 1
            den = 6 + 4 * j * (j + 1)
            r = 1 / den
            x = (-8 * j - 4) / den
            y = 9 / den
            self.green_circles.append(Circle(self, center=[x, y, 0], radius=r, thickness=thickness*np.sqrt(6*r), color=colors[1],
                                             name='green_circle_' + str(i)))

        for i in range(1, details + 1):
            den = 15 + 4 * i * (i - 1)
            r = 1 / den
            x = (8 * i - 4) / den
            y = 15 / den
            self.blue_circles.append(Circle(self, center=[x, y, 0], radius=r, thickness=thickness*np.sqrt(6*r), color=colors[2],
                                            name='blue_circle_' + str(i)))
            j = i - 1
            den = 15 + 4 * j * (j + 1)
            r = 1 / den
            x = (-8 * j - 4) / den
            y = 15 / den
            self.blue_circles.append(Circle(self, center=[x, y, 0], radius=r, thickness=thickness*np.sqrt(6*r), color=colors[2],
                                            name='blue_circle_' + str(i)))

    def appear(self,
               begin_times=[0],
               transition_times=[1],
               **kwargs):

        self.begin_times = begin_times

        super().appear(begin_time=begin_times[0], transition_time=0, empty=True)
        for index, circle in enumerate(self.red_circles):
            if index >= len(begin_times):
                index = -1
            if index >= len(transition_times):
                index2 = -1
            else:
                index2 = index
            circle.grow(begin_time=begin_times[index], transition_time=transition_times[index2])

        for index in range(len(self.green_circles)):
            i = index
            if index >= len(begin_times) - 1:
                index = -2
            if index >= len(transition_times) - 1:
                index2 = -2
            else:
                index2 = index
            self.green_circles[i].grow(begin_time=begin_times[index + 1], transition_time=transition_times[index2 + 1])
            self.blue_circles[i].grow(begin_time=begin_times[index + 1], transition_time=transition_times[index2 + 1])

    def get_center(self, index):
        if index % 2 == 0:
            index /= 2
            den = 2 + index * index
            x = 2 * index / den
            y = 3 / den
        else:
            index += 1
            index /= 2
            den = 2 + index * index
            x = -2 * index / den
            y = 3 / den
        return self.coords2location([x, y])

    def get_scale(self, index):
        index += 1
        index /= 2
        index = int(index)
        den = 2 + index * index
        return 1 / den

    def get_begin_time(self, index):
        if self.begin_times is None:
            print("logo appearance has to be set before the function is called ")
            return 0
        if index >= len(self.begin_times):
            index = -1
        return self.begin_times[index]

    def get_world_matrix(self):
        return self.ref_obj.matrix_world


class LogoPreImage(BObject):
    def __init__(self,**kwargs):
        self.kwargs = kwargs
        circles=[]
        circles2=[]
        circles3=[]
        thickness=0.05
        extrude=0.1
        dim = self.get_from_kwargs('dim',5)
        for i in range(0,dim+1):
            circle = Circle2(center=[(2*i-1)/4,9/16],radius=1/16,color='drawing',thickness= thickness,extrude=extrude)
            circles.append(circle)
            circle = Circle2(center=[(-2*i-1)/4,9/16],radius=1/16,color='drawing',thickness= thickness,extrude=extrude)
            circles.append(circle)
        for i in range(0,dim+1):
            circle = Circle2(center=[(2*i-1)/4,15/16],radius=1/16,color='joker',thickness= thickness,extrude=extrude)
            circles2.append(circle)
            circle = Circle2(center=[(-2*i-1)/4,15/16],radius=1/16,color='joker',thickness= thickness,extrude=extrude)
            circles2.append(circle)
        for i in range(0,dim+1):
            circle = Circle2(center=[(i-1)/2,3/4],radius=1/4,color='important',thickness= 2*thickness,extrude=extrude)
            circles3.append(circle)
            circle = Circle2(center=[(-i-1)/2,3/4],radius=1/4,color='important',thickness= 2*thickness,extrude=extrude)
            circles3.append(circle)
        super().__init__(children=[*circles,*circles2,*circles3],name="Logo",**kwargs,color='important')

    def appear(self,
               begin_time=0,
               transition_time=0,
               **kwargs):

        super().appear(begin_time=begin_time,transition_time=transition_time)
        dt = transition_time/len(self.b_children)

        t0 = begin_time
        delta = int(len(self.b_children)/3)
        for i in range(delta):
            self.b_children[i].grow(begin_time=t0,transition_time=dt)
            self.b_children[i+delta].grow(begin_time=t0,transition_time=dt)
            self.b_children[i+2*delta].grow(begin_time=t0,transition_time=dt)
            t0+=dt

    def transform(self,transformation, begin_time=0, transition_time=DEFAULT_ANIMATION_TIME):
        for child in self.b_children:
            child.transform(transformation,begin_time=begin_time,transition_time=transition_time)