import functools
import inspect
import os
import warnings
from copy import deepcopy
from datetime import datetime

import bpy
import numpy as np

from appearance.textures import make_basic_material, make_creature_material, make_translucent_material, \
    make_fake_glass_material, make_plastic_material, make_checker_material, make_mirror_material, make_sand_material, \
    make_gold_material, make_silver_material, make_screen_material, make_marble_material, make_metal_materials, \
    make_wood_material, make_scattering_material, make_silk_material, make_magnet_material, make_sign_material
from interface.ibpy import select, link, delete, Vector, Quaternion
from utils.constants import COLORS, COLOR_NAMES

pi = np.pi

def get_from_dictionary(dictionary,string_list):
    objects=[]
    for string in string_list:
        if string in dictionary:
            objects.append(dictionary[string])

    return objects


def retrieve_name(var):
    """
    This function can be used to create a dictionary of local variables
    An example can be found in
    experiments/variable_name_to_string.py
    bwm/scene_bwm.py
    """
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]


def z2p(z):
    return [np.real(z), np.imag(z)]


def z2vec(z,z_dir=False):
    if z_dir:
        return Vector([np.real(z),0,np.imag(z)])
    return Vector([np.real(z),np.imag(z),0])


def p2z(p):
    return p[0] + 1j * p[1]


def re(z):
    return np.real(z)


def im(z):
    return np.imag(z)


def z2str(z):
    string = ''
    if np.real(z) == 0 and np.imag(z) == 0:
        return "0"
    if np.real(z) != 0:
        re = np.real(z)
        if re == np.round(re):
            string += str(int(re))
        else:
            string += str(re)
    if np.imag(z) == 0:
        return string
    if np.imag(z) > 0:
        string += '+'
    else:
        string += '-'
    if np.abs(np.imag(z)) == 1:
        string += 'i'
        return string
    im = np.abs(np.imag(z))
    if im == np.round(im):
        string += (str(int(im)) + 'i')
    else:
        string += (str(im) + 'i')
    return string


def to_vector(z):
    if z is None:
        return z
    if not isinstance(z,Vector):
        return Vector(z)
    else:
        return z


def to_list(l):
    if isinstance(l,list):
        return l
    else:
        return [l]

def flatten(colors):
    colors_flat = [col for sublist in colors for col in sublist]
    return colors_flat


"""
    translated methods
"""


def quaternion_from_normal(normal):
    normal.normalize()
    angle = np.arccos(normal.dot(Vector([0, 0, 1])))
    axis = Vector([0, 0, 1]).cross(normal)
    length = axis.length
    if length == 0:
        raise "error: rotation axis not found"
    axis /= length
    quaternion = Quaternion([np.cos(angle / 2), *((axis * np.sin(angle / 2))[:])])
    return quaternion


def link_descendants(obj, unlink=False, top_level=True):
    # If children exist, link those too
    # Will break if imported children were linked in add_to_blender
    # (if their object name in blender is the same as the filename)

    if unlink and top_level:
        select(obj)
        # obj.select = True
    # obj_names=[x.name for x in bpy.data.objects]
    obj_names = []
    for child in obj.children:
        if not unlink:
            if child.name not in obj_names:
                link(child)
        else:
            child.select = True
        link_descendants(child, unlink=unlink, top_level=False)
    if unlink:
        delete()


"""
untranslated methods
"""
def get_save_length(start, end):
    if isinstance(start, list):
        start = Vector(start)
    if isinstance(end, list):
        end = Vector(end)
    return (end - start).length


def get_rotation_quaternion_from_start_and_end(start, end):
    """
    For simplicity this works for an object that is of unit length directed in z-direction
    :param start:
    :param end:
    :return:
    """
    if isinstance(start, list):
        start = Vector(start)
    if isinstance(end, list):
        end = Vector(end)

    diff = to_vector(end - start)
    diff = diff.normalized()
    up = Vector((0, 0, 1))  # default orientation
    axis = up.cross(diff).normalized()
    if axis.length == 0:
        if diff.dot(up) > 0:
            return Quaternion()  # no rotation is needed
        else:
            return Quaternion([0, 0, 1, 0])  # rotation by 180 degrees
    angle = np.arccos(up.dot(diff))
    quaternion_axis = axis * np.sin(angle / 2)
    quaternion = Quaternion([np.cos(angle / 2), *quaternion_axis[:]])

    return quaternion


def define_materials():
    if 'default' not in bpy.data.materials:
        mat = bpy.data.materials.new(name='default')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.8, 1, 1, 1)

    for i, col_name in enumerate(COLOR_NAMES):
        name = col_name
        col = COLORS[i]
        make_basic_material(rgb=deepcopy(col), name=name)
        name = 'creature_color' + str(i + 1)
        make_creature_material(rgb=deepcopy(col), name=name)
        name = 'glass_' + col_name
        make_translucent_material(rgb=deepcopy(col), name=name)
        name='fake_glass_'+col_name
        make_fake_glass_material(rgb=deepcopy(col),name=name)
        name='plastic_'+col_name
        make_plastic_material(rgb=deepcopy(col),name=name)

    # create checker material
    make_checker_material()
    make_mirror_material()
    make_sand_material()
    make_gold_material()
    make_silver_material()
    make_screen_material()
    make_marble_material()
    make_metal_materials()
    make_wood_material()
    make_scattering_material()
    make_silk_material()
    make_magnet_material()
    make_sign_material()

def finish_noise(error=False):
    if error:
        os.system('spd-say "your program has finished with errors"')
    else:
        os.system(
            'spd-say "your program has successfully finished"')  # https://stackoverflow.com/questions/16573051/python-sound-alarm-when-code-finishes


'''
Time measurement
'''
TIME_LIST = []
now = datetime.now()
TIME_LIST.append(now)
TIME_REPORT = []


def execute_and_time(message, *funcs):  # Not sure how this will work for more than one bobject that returns
    outputs = []
    for func in funcs:
        output = func
        if output is not None:
            outputs.append(output)

    local_now = datetime.datetime.now()
    TIME_LIST.append(local_now)  # Actually just records end time, not start and end
    # So reported value includes previous, seemingly untimed code
    diff = TIME_LIST[-1] - TIME_LIST[-2]
    TIME_REPORT.append([diff.total_seconds(), message])
    if not outputs:
        return
    if len(outputs) == 1:
        outputs = outputs[0]
    return outputs


def print_time_report():
    print()
    for line in TIME_REPORT:
        print(line[0], line[1])
    local_now = datetime.now()
    total = local_now - TIME_LIST[0]
    print(total.total_seconds(), "Total")


def add_lists_by_element(list1, list2, subtract=False):
    if len(list1) != len(list2):
        raise Warning("The lists aren't the same length")
    list3 = list(deepcopy(list2))
    if subtract:
        for i in range(len(list3)):
            list3[i] *= -1
    return list(map(sum, zip(list1, list3)))


def mult_lists_by_element(vec1, vec2, divide=False):
    vec3 = []
    if not divide:
        for x1, x2, in zip(vec1, vec2):
            vec3.append(x1 * x2)
    else:
        for x1, x2, in zip(vec1, vec2):
            vec3.append(x1 / x2)

    return vec3


'''
Animation helpers
'''


def make_animations_linear(thing_with_animation_data, data_paths=None, extrapolate=False):
    if data_paths is None:
        f_curves = thing_with_animation_data.animation_data.action.fcurves
    else:
        f_curves = []
        for fc in thing_with_animation_data.animation_data.action.fcurves:
            if fc.data_path in data_paths:
                f_curves.append(fc)
    for fc in f_curves:
        if extrapolate:
            fc.extrapolation = 'LINEAR'  # Set extrapolation type
        # Iterate over this fcurve's keyframes and set handles to vector
        for kp in fc.keyframe_points:
            kp.handle_left_type = 'VECTOR'
            kp.handle_right_type = 'VECTOR'
            kp.interpolation = 'LINEAR'


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the bobject is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated bobject {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


#
#     # Blinks
#     ref_obj = new_bobject.ref_obj
#     if filename == 'boerd_blob' or filename == 'boerd_blob_squat' or filename == 'blob':
#         leye = ref_obj.children[0].children[-2]
#         reye = ref_obj.children[0].children[-3]
#         if filename == 'blob':
#             leye = ref_obj.children[0].children[0]
#             reye = ref_obj.children[0].children[1]
#         blink_action = bpy.data.actions.new('Blinks')
#         if ref_obj.children[0].animation_data.action == None:
#             ref_obj.children[0].animation_data_create()
#         ref_obj.children[0].animation_data.action = blink_action
#         # reye.animation_data_create()
#         # reye.animation_data.action = blink_action
#
#         leye = ref_obj.children[0].pose.bones[5]
#         reye = ref_obj.children[0].pose.bones[6]
#         if filename == 'blob':
#             leye = ref_obj.children[0].pose.bones[-2]
#             reye = ref_obj.children[0].pose.bones[-3]
#         t = 0
#         if 'cycle_length' not in kwargs:
#             cycle_length = BLINK_CYCLE_LENGTH
#         else:
#             cycle_length = kwargs['cycle_length']
#
#         leye.keyframe_insert(data_path='scale', frame=0)
#         leye.keyframe_insert(data_path='scale', frame=BLINK_CYCLE_LENGTH)
#         reye.keyframe_insert(data_path='scale', frame=0)
#         reye.keyframe_insert(data_path='scale', frame=BLINK_CYCLE_LENGTH)
#
#         while t < cycle_length - BLINK_LENGTH:
#             blink_roll = random()
#             if blink_roll < BLINK_CHANCE:
#                 leye.keyframe_insert(data_path='scale', frame=t)
#                 leye.scale[1] = 0.2
#                 frm = mathematics.floor(BLINK_LENGTH / 2) - 1
#                 leye.keyframe_insert(data_path='scale', frame=t + frm)
#                 frm = mathematics.ceil(BLINK_LENGTH / 2) + 1
#                 leye.keyframe_insert(data_path='scale', frame=t + frm)
#                 leye.scale[1] = 1
#                 leye.keyframe_insert(data_path='scale', frame=t + BLINK_LENGTH)
#
#                 reye.keyframe_insert(data_path='scale', frame=t)
#                 reye.scale[1] = 0.2
#                 frm = mathematics.floor(BLINK_LENGTH / 2) - 1
#                 reye.keyframe_insert(data_path='scale', frame=t + frm)
#                 frm = mathematics.ceil(BLINK_LENGTH / 2) + 1
#                 reye.keyframe_insert(data_path='scale', frame=t + frm)
#                 reye.scale[1] = 1
#                 reye.keyframe_insert(data_path='scale', frame=t + BLINK_LENGTH)
#
#                 t += BLINK_LENGTH
#
#             else:
#                 t += 1
#         # Make blinks cyclical
#         '''try:
#             leye_fcurve = ref_obj.children[0].animation_data.action.fcurves.find(
#                 'pose.bones["brd_bone_eye.l"].scale',
#                 index = 1
#             )
#             l_cycle = leye_fcurve.modifiers.new(type = 'CYCLES')
#             #l_cycle.blend_out = BLINK_CYCLE_LENGTH
#
#             reye_fcurve = ref_obj.children[0].animation_data.action.fcurves.find(
#                 'pose.bones["brd_bone_eye.r"].scale',
#                 index = 1
#             )
#             r_cycle = reye_fcurve.modifiers.new(type = 'CYCLES')
#             #r_cycle.blend_out = BLINK_CYCLE_LENGTH
#         except:
#             #Sometimes a creature goes the whole cycle length without blinking,
#             #in which case, there's no fcurve, so the above block throws an
#             #error. In the end, it's fine if the creature never blinks. It's rare.
#             pass'''
#
#     # Wiggles
#     if 'wiggle' in kwargs:
#         wiggle = kwargs['wiggle']
#     else:
#         wiggle = False
#     if (filename == 'boerd_blob' or filename == 'boerd_blob_squat' or filename == 'blob') \
#             and wiggle == True:
#         wiggle_action = bpy.data.actions.new('Wiggles')
#         if ref_obj.children[0].animation_data.action == None:
#             ref_obj.children[0].animation_data_create()
#         ref_obj.children[0].animation_data.action = wiggle_action
#
#         if 'cycle_length' not in kwargs:
#             wiggle_cycle_length = BLINK_CYCLE_LENGTH
#         else:
#             wiggle_cycle_length = int(kwargs['cycle_length'])
#         wiggle_slow_factor = 1
#         wind_down_time = FRAME_RATE / wiggle_slow_factor
#
#         new_bobject.head_angle = [None] * wiggle_cycle_length
#         new_bobject.head_angle_vel = [None] * wiggle_cycle_length
#         for t in range(wiggle_cycle_length):
#             if t == 0:
#                 # Start in neutral position
#                 new_bobject.head_angle[t] = [
#                     1,
#                     uniform(0, 0),
#                     uniform(0, 0),
#                     uniform(0, 0),
#                 ]
#                 new_bobject.head_angle_vel[t] = [
#                     0,
#                     uniform(-0.0025, 0.0025),
#                     uniform(-0.0025, 0.0025),
#                     uniform(-0.0025, 0.0025)
#                 ]
#                 bone = ref_obj.children[0].pose.bones[3]
#                 bone.rotation_quaternion = new_bobject.head_angle[t]
#                 bone.keyframe_insert(
#                     data_path="rotation_quaternion",
#                     frame=t * wiggle_slow_factor
#                 )
#             elif t < wiggle_cycle_length - wind_down_time:
#                 # Random movement up to a half second before end of cycle.
#                 # update position
#                 a = new_bobject.head_angle[t - 1]
#                 b = new_bobject.head_angle_vel[t - 1]
#                 new_bobject.head_angle[t] = list(mappings(sum, zip(a, b)))
#
#                 # Hard max on head angles
#                 extrema = [
#                     [1, 1],
#                     [-0.05, 0.05],
#                     [-0.05, 0.05],
#                     [-0.05, 0]
#                 ]
#                 a = new_bobject.head_angle[t]
#                 for i in range(1, len(new_bobject.head_angle[t])):
#                     if a[i] < extrema[i][0]:
#                         a[i] = extrema[i][0]
#                     if a[i] > extrema[i][1]:
#                         a[i] = extrema[i][1]
#
#                 # update velocity to be used when updating position
#                 # in next frame
#                 a = new_bobject.head_angle_vel[t - 1]
#                 b = [
#                     0,
#                     uniform(-0.0005, 0.0005),
#                     uniform(-0.0005, 0.0005),
#                     uniform(-0.0005, 0.0005)
#                 ]
#                 # Shift the acceleration distribution toward neutral
#                 for i in range(1, len(b)):
#                     go_back = -new_bobject.head_angle[t][i] / 5000
#                     b[i] += go_back
#                 new_bobject.head_angle_vel[t] = list(mappings(sum, zip(a, b)))
#
#                 bone = ref_obj.children[0].pose.bones[3]
#                 bone.rotation_quaternion = new_bobject.head_angle[t]
#                 bone.keyframe_insert(
#                     data_path="rotation_quaternion",
#                     frame=t * wiggle_slow_factor
#                 )
#             else:
#                 # Approach neutral toward end of cycle, for continuity across
#                 # scenes
#                 # update position
#                 a = new_bobject.head_angle[t - 1]
#                 b = new_bobject.head_angle_vel[t - 1]
#                 new_bobject.head_angle[t] = list(mappings(sum, zip(a, b)))
#
#                 # Hard max on head angles
#                 extrema = [
#                     [1, 1],
#                     [-0.1, 0.1],
#                     [-0.1, 0.1],
#                     [-0.1, 0]
#                 ]
#                 a = new_bobject.head_angle[t]
#                 for i in range(1, len(new_bobject.head_angle[t])):
#                     if a[i] < extrema[i][0]:
#                         a[i] = extrema[i][0]
#                         if b[i] < 0: b[i] = 0
#                     if a[i] > extrema[i][1]:
#                         a[i] = extrema[i][1]
#                         if b[i] > 0: b[i] = 0
#
#                 # update velocity to be used when updating position
#                 # in next frame
#                 # Calculate acceleration needed to get back to neutral
#
#                 time_left = wiggle_cycle_length - t
#                 timing_factor = (wind_down_time - time_left) * time_left \
#                                 / wind_down_time ** 2
#                 target_v = [  # Approaches zero as distance goes to zero
#                     - a[1] * timing_factor,
#                     - a[2] * timing_factor,
#                     - a[3] * timing_factor,
#                 ]
#
#                 acc_x = (target_v[0] - b[1]) / 2
#                 acc_y = (target_v[1] - b[2]) / 2
#                 acc_z = (target_v[2] - b[3]) / 2
#
#                 a = new_bobject.head_angle_vel[t - 1]
#                 b = [
#                     0,
#                     acc_x,
#                     acc_y,
#                     acc_z,
#                 ]
#
#                 new_bobject.head_angle_vel[t] = list(mappings(sum, zip(a, b)))
#
#                 bone = ref_obj.children[0].pose.bones[3]
#                 bone.rotation_quaternion = new_bobject.head_angle[t]
#                 bone.keyframe_insert(
#                     data_path="rotation_quaternion",
#                     frame=t * wiggle_slow_factor
#                 )
#
#         # Make wiggle cyclical
#         '''bone_x_fcurve = ref_obj.children[0].animation_data.action.fcurves.find(
#             'pose.bones["brd_bone_neck"].rotation_quaternion',
#             index = 0
#         )
#         neck_x_cycle = bone_x_fcurve.modifiers.new(type = 'CYCLES')
#         neck_x_cycle.frame_start = 0
#         neck_x_cycle.frame_end = wiggle_cycle_length * wiggle_slow_factor
#
#         bone_y_fcurve = ref_obj.children[0].animation_data.action.fcurves.find(
#             'pose.bones["brd_bone_neck"].rotation_quaternion',
#             index = 1
#         )
#         neck_y_cycle = bone_y_fcurve.modifiers.new(type = 'CYCLES')
#         neck_y_cycle.frame_start = 0
#         neck_y_cycle.frame_end = wiggle_cycle_length * wiggle_slow_factor
#
#         bone_z_fcurve = ref_obj.children[0].animation_data.action.fcurves.find(
#             'pose.bones["brd_bone_neck"].rotation_quaternion',
#             index = 2
#         )
#         neck_z_cycle = bone_z_fcurve.modifiers.new(type = 'CYCLES')
#         neck_z_cycle.frame_start = 0
#         neck_z_cycle.frame_end = wiggle_cycle_length * wiggle_slow_factor'''
#
#     if filename == 'stanford_bunny':
#         eye = ref_obj.children[0].children[0]
#         t = 0
#         while t < BLINK_CYCLE_LENGTH:
#             blink_roll = random()
#             if blink_roll < BLINK_CHANCE:
#                 eye.keyframe_insert(data_path='scale', frame=t)
#                 eye.scale[1] = 0.2
#                 frm = mathematics.floor(BLINK_LENGTH / 2) - 1
#                 eye.keyframe_insert(data_path='scale', frame=t + frm)
#                 frm = mathematics.ceil(BLINK_LENGTH / 2) + 1
#                 eye.keyframe_insert(data_path='scale', frame=t + frm)
#                 eye.scale[1] = 1
#                 eye.keyframe_insert(data_path='scale', frame=t + BLINK_LENGTH)
#
#                 t += BLINK_LENGTH
#             else:
#                 t += 1
#         # Make blinks cyclical
#         try:
#             eye_fcurve = ref_obj.children[0].children[0].animation_data.action.fcurves.find(
#                 'scale',
#                 index=1
#             )
#             cycle = eye_fcurve.modifiers.new(type='CYCLES')
#             cycle.frame_start = 0
#             cycle.frame_end = BLINK_CYCLE_LENGTH
#         except:
#             # Sometimes a creature goes the whole cycle length without blinking,
#             # in which case, there's no fcurve, so the above block throws an
#             # error. In the end, it's fine if the creature never blinks. It's rare.
#             pass
#
#     return new_bobject
