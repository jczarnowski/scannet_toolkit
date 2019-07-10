import sys
sys.path.insert(0,'./PyGLer/src')
sys.path.insert(0,'./PyGLer/src/pygler/gui')

#from utils import ComputeNormals
import pygler

import os
import cv2
import glob
import argparse

pygler.VertexShaderCode = \
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


pygler.FragmentShaderCode = \
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

from pygler.viewer import *
from pygler.utils import CreateAxisModel, CreateCubeModel, ComputeNormals, CameraParams

def LoadPly(filename, computeNormals=True, autoScale=False):
    '''
    Load vertices and faces from a wavefront .obj file and generate normals.
    '''
    from plyfile import PlyData, PlyElement
    plydata = PlyData.read(filename)

    # Get vertices and faces
    vertices = np.stack([plydata['vertex']['x'],plydata['vertex']['y'],plydata['vertex']['z']],axis=1).astype(np.float32)
    faces = np.transpose(np.stack(plydata['face']['vertex_indices']),[0,1]).astype(np.uint32)

    #normals = np.stack([plydata['vertex']['nx'],plydata['vertex']['ny'],plydata['vertex']['nz']],axis=1).astype(np.float32)
    normals = None
    if computeNormals:
        normals = ComputeNormals(vertices,faces)

    geometry = Geometry(vertices, triangles=faces, normals=normals,autoScale=autoScale)
    return PyGLerModel(filename, geometry)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', required=True)
    args = parser.parse_args()

    import tqdm

    # look up all scene directories
    scene_dirs = sorted(glob.glob(os.path.join(args.data_dir, '*/')))[0::2]

    print('Found {} scenes'.format(len(scene_dirs)))

    camParams = CameraParams(width=640,height=480,cx=319.500000,cy=239.500000,fx=571.623718,fy=571.623718,znear=0.001,zfar=10000.0,unit=1.0)
    viewer = PyGLer(useFBO=True, cameraParams=camParams)
    viewer.start()

    #with viewer.lock:
    #    viewer.shader = Shader(VertexShaderCode,  FragmentShaderCode)
    #    viewer.shader.bind()
    #    viewer.shader.uniform_matrixf("projM", projMat)

    for scene_num, scene_dir in enumerate(scene_dirs):
        scenename = os.path.basename(os.path.normpath(scene_dir))

        print('Rendering {} [{}/{}]'.format(scenename, scene_num, len(scene_dirs)))
        tri = LoadPly(os.path.join(scene_dir, '{}_vh_clean_2.ply'.format(scenename)), autoScale=False)
        viewer.addModel(tri)
        
        # check trajectory length
        n = len(glob.glob(os.path.join(scene_dir, '*.color.jpg')))

        for i in tqdm.tqdm(range(0,n)):
            pose = np.loadtxt(os.path.join(scene_dir, 'frame-{:06d}.pose.txt'.format(i)))
            tri.setModelM(np.linalg.inv(pose))
            
            viewer.redraw()

            depth, bgr = viewer.Convert2BGRD(viewer.capture())
            bgr = (bgr * np.iinfo(np.uint16).max).astype(np.uint16)

            bgr_file = os.path.join(scene_dir, 'frame-{:06d}.rendered_normal.png'.format(i))
            depth_file = os.path.join(scene_dir, 'frame-{:06d}.rendered_depth.png'.format(i))

            cv2.imwrite(bgr_file, bgr)
            cv2.imwrite(depth_file, depth)

        viewer.removeAll()
            
            
viewer.removeModel(tri)
