# Imports:
from typing import Any

import bpy
import bmesh
import numpy as np
import colorsys

def mandelbrot(z):
    it = 100
    count =0
    w = 0
    threshold = 10
    while count<it and threshold>np.abs(w):
        w = w*w+z
        count+=1
    if count==it:
        return it
    else: 
        phase = np.pi*(it-count)/it
        return count*np.exp(1j*phase)

def sin(z):
    return np.sin(z)

def sphere2plane(r,x,y,z):
    return r*x/(r-z)+1j*r*y/(r-z)


def new_sphere(r, level, function):
    
    subdivisions = 2**level
    
    #bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=radius, enter_editmode=False, align='WORLD', location=(0, 0, 0)) 
    bpy.ops.mesh.primitive_uv_sphere_add(segments=subdivisions, ring_count=subdivisions, radius=r, enter_editmode=False, location=(0, 0, 0))  
    obj = bpy.context.active_object  # Selects the sphere
    me = bpy.context.active_object.data  # Selects the data of the sphere

    bm = bmesh.new()   # Creates an empty BMesh
    bm.from_mesh(me)   # Fills it in using the plane 
    
    
    #rotate sphere to regularize poles
    epsilon = 0.01
    #print("Before rotation:")
    for v in bm.verts:
        x = v.co.x
        y= v.co.y
        z= v.co.z
        
        #perform tiny rotation to regularize the poles
        rot = np.array([[np.cos(epsilon), 0,np.sin(-epsilon)],[0,1,0], [np.sin(epsilon), 0,np.cos(epsilon)]])
        vec = np.array([x,y,z])
        vec2 = np.matmul(rot,vec)
        
        v.co = vec2
       
    bm.to_mesh(me)  # Freeing the BMesh, moving on to coloring the domain
    bm.free()

    # Assigning color to the vertices:

    vert_list = me.vertices
    color_map_collection = me.vertex_colors

    if len(color_map_collection) == 0:   # Creates a new color map or replaces 
                                           # the current one under name 'Col'
        color_map_collection.new()

    color_map = color_map_collection['Col']

    i = 0
    for poly in me.polygons:               
        for idx in poly.loop_indices:
                                          # For loop used for coloring each vertex  
            loop = me.loops[idx]
            
            v = loop.vertex_index
            
            # Z is the complex coordinate after projection the point on the sphere back to the complex plane            
            Z = sphere2plane(r,vert_list[v].co.x,vert_list[v].co.y,vert_list[v].co.z) 
            angle = np.angle(function(Z))  # Returns the phase of the complex number
        
            final = colorsys.hsv_to_rgb(0.5+0.5*angle/np.pi,1,1)
            color_map.data[i].color = (*final,0)
            i += 1
    
    # Connecting the Vertex Color node output to the default Principled BSDF base color input
    # to see color in rendered view:
    phase_color = bpy.data.materials.new(name="Phase Color")
    phase_color.use_nodes = True
    nodes = phase_color.node_tree.nodes
    p_bsdf = nodes.get("Principled BSDF")
    vert_col = nodes.new(type='ShaderNodeVertexColor')
    links = phase_color.node_tree.links
    links.new(vert_col.outputs[0], p_bsdf.inputs[0])
    bpy.context.object.active_material = phase_color

    # Setting to object mode:
    bpy.ops.object.mode_set(mode='OBJECT')
            
    return obj


def create_profile_shape_key(object,function,log):
    verts = object.data.vertices

    if object.data.shape_keys ==None:
        sk_basis = object.shape_key_add(name='Basis')
        sk_basis.interpolation = 'KEY_LINEAR'
        object.data.shape_keys.use_relative = True


    sk = object.shape_key_add(name='Profile')
    sk.interpolation = 'KEY_LINEAR'

    #calculate radius
    x,y,z = sk.data[0].co[:]
    r = np.sqrt(x*x+y*y+z*z)
  
    # position each vert
    for i in range(len(verts)):
        x,y,z=sk.data[i].co[:]
        
        Z = sphere2plane(r,x,y,z)

        mag = np.abs(function(Z))
        l_mag = np.log(mag)/np.log(10) # Returns the phase of the complex number
     
        if log:
            if l_mag<0:
                sk.data[i].co = 1/(1-l_mag) *sk.data[i].co
            else:
                sk.data[i].co = (1+l_mag)*sk.data[i].co 
        else:
            sk.data[i].co = mag*sk.data[i].co

sphere = new_sphere(w,8,mandelbrot)
#add shape keys
create_profile_shape_key(sphere,mandelbrot,True)