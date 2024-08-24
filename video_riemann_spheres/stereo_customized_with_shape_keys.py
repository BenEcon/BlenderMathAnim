import bpy, bmesh
from mathutils import Vector

###################got this from mesh_looptools.py#################

# input: bmesh, output: dict with the edge-key as key and face-index as value
def dict_edge_faces(bm):
    edge_faces = dict([[edgekey(edge), []] for edge in bm.edges 
                                        if not edge.hide])
    for face in bm.faces:
        if face.hide:
            continue
        for key in face_edgekeys(face):
            edge_faces[key].append(face.index)

    return(edge_faces)


# return the edgekey ([v1.index, v2.index]) of a bmesh edge
def edgekey(edge):
    return(tuple(sorted([edge.verts[0].index, edge.verts[1].index])))

# returns the edgekeys of a bmesh face
def face_edgekeys(face):
    return([tuple(sorted([edge.verts[0].index, edge.verts[1].index])) for \
        edge in face.edges])


###################################################################


def stereo_proj(scale_factor=0.9):


    verts = obj.data.vertices

    sk_basis = obj.shape_key_add(name='Basis')
    sk_basis.interpolation = 'KEY_LINEAR'
    obj.data.shape_keys.use_relative = True


    sk = obj.shape_key_add(name='Deform')
    sk.interpolation = 'KEY_LINEAR'


     # position each vert
    for i in range(len(verts)):
        x,y,z=sk.data[i].co[:]
        r2 = x*x + y*y
        nv = 1./(r2 + 1) * Vector((2*x, 2*y, (r2 - 1)))
        sk.data[i] = nv

#    # Create 10 sequential deformations
#    for n in range(10):
#        # Create new shape key
#        

#       

#    # Get the active mesh
#    me = bpy.context.object.data
#    # Get a BMesh representation
#    bm = bmesh.new()   
#    bm.from_mesh(me)   

#    
#    for v in bm.verts:
#        x,y,z = v.co[:]
#        r2 = x*x + y*y
#        nv = 1./(r2 + 1) * Vector((2*x, 2*y, (r2 - 1)))
#        v.co = nv
#           
#    # Finish up, write the bmesh back to the mesh
#    bm.to_mesh(me)
#    bm.free()  

obj = bpy.context.active_object
stereo_proj()