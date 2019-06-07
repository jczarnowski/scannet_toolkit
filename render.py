import sys
sys.path.insert(0,'./PyGLer/src')
sys.path.insert(0,'./PyGLer/src/pygler/gui')

#from utils import ComputeNormals
import pygler
from pygler.viewer import *
from pygler.utils import CreateAxisModel, CreateCubeModel, ComputeNormals

import os
import cv2
import glob
import argparse

VertexShaderCode = \
"""
#version 130
uniform vec4 singleColor;
uniform mat4 projM;
uniform mat4 viewM;
uniform mat4 modelM;
in vec4 position;
in vec4 color;
out vec4 vcolor;
out vec4 vposition;
void main() {
    mat3 modelM_rot = mat3(modelM);
    
    gl_Position = projM * viewM * modelM * position;
    vposition = gl_Position;
    if(singleColor.x==-1.0)
    {
        vec3 vcolor_ = (modelM_rot*color.rgb+1.0)/2.0;
        vcolor.rgb = vcolor_;
        vcolor.a = 1.0;
    }
    else
    {
        vcolor = singleColor;
    }
}
"""


FragmentShaderCode = \
"""
#version 130
in vec4 vcolor;
in vec4 vposition;
out vec4 fragColor;
out vec4 fragPos;
void main() {
    fragColor = vcolor;
    fragPos = vposition;

}
"""

def LoadPly(filename, computeNormals=True, autoScale=False):
    '''
    Load vertices and faces from a wavefront .obj file and generate normals.
    '''
    from plyfile import PlyData, PlyElement
    plydata = PlyData.read(filename)

    # Get vertices and faces
    vertices = np.stack([plydata['vertex']['x'],plydata['vertex']['y'],plydata['vertex']['z']],axis=1).astype(np.float32)
    faces = np.transpose(np.stack(plydata['face']['vertex_indices']),[0,1]).astype(np.uint32)

    print(faces.shape)
    #normals = np.stack([plydata['vertex']['nx'],plydata['vertex']['ny'],plydata['vertex']['nz']],axis=1).astype(np.float32)
    normals = None
    if computeNormals:
        from utils import ComputeNormals
        normals = ComputeNormals(vertices,faces)

    geometry = Geometry(vertices, triangles=faces, normals=normals,autoScale=autoScale)
    return PyGLerModel(filename, geometry)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', required=True)
    args = parser.parse_args()

    # look up all scene directories
    scene_dirs = glob.glob(os.path.join(args.data_dir, '*/'))
    print('Found {} scenes'.format(len(scene_dirs)))

    viewer = PyGLer(useFBO=True)
    viewer.start()
    for scenedir in scene_dirs:
        scenename = os.path.basename(os.path.normpath(scenedir))

        print('Rendering ', scenename)
        tri = PyGLerModel.LoadPly(os.path.join(scene_dir, '{}_vh_clean_2.ply'.format(scene_dir, scenename)), autoScale=False)
        viewer.addModel(tri)
        
        # check trajectory length
        n = len(glob.glob(os.path.join(scenedir, '*.color.jpg')))
        print('Trajectory length is ', n)

        for i in range(0,n):
            pose = np.loadtxt(os.path.join(scenedir, 'frame-{:06d}.pose.txt'.format(i)))
            tri.setModelM(np.linalg.inv(pose))
            
            depth, bgr = viewer.Convert2BGRD(viewer.capture())

            # do we want resizing here? then do rgb too
            #bgr = cv2.resize(bgr,(256,192),interpolation=cv2.INTER_NEAREST)
            #depth = cv2.resize(depth,(256,192),interpolation=cv2.INTER_NEAREST)

            np.save(os.path.join(scene_dir, 'rendered_normal_{:06d}.npy'.format(i)), bgr.astype(np.float32))
            np.save(os.path.join(scene_dir, 'rendered_depth_{:06d}.npy'.format(i)), depth)

            viewer.redraw()
            
viewer.removeModel(tri)
