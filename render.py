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
#version 140
uniform vec4 singleColor;
uniform mat4 projM;
uniform mat4 viewM;
uniform mat4 modelM;
in vec4 position;
in vec4 color;
out vec4 vcolor;
out vec4 vposition;
void main() {
    mat4 VM = viewM * modelM;
    vposition = projM * VM * position;
    vec3 out_col = (mat3(VM) * -(color.rgb * 2 - 1) + 1) / 2.0;
    vcolor = vec4(out_col, 1.0);
    gl_Position = vposition;
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
    parser.add_argument('--save_normals', default=False, action='store_true')
    args = parser.parse_args()

    import tqdm

    # look up all scene directories
    scene_dirs = sorted(glob.glob(os.path.join(args.data_dir, '*/')))

    print('Found {} scenes'.format(len(scene_dirs)))

    camParams = CameraParams(width=640,height=480,cx=319.500000,cy=239.500000,fx=571.623718,fy=571.623718,znear=0.001,zfar=10000.0,unit=1.0)
    viewer = PyGLer(useFBO=True, cameraParams=camParams)
    viewer.start()

    for scene_num, scene_dir in enumerate(scene_dirs):
        scenename = os.path.basename(os.path.normpath(scene_dir))

        # check trajectory length
        with open(os.path.join(scene_dir, '_info.txt')) as f:
            n = int(f.readlines()[-1].split(' ')[-1])
        #n = len(glob.glob(os.path.join(scene_dir, '*.color.jpg')))

        depth_done = os.path.exists(os.path.join(scene_dir, 'frame-{:06d}.rendered_depth.png'.format(n-1)))
        normals_done = os.path.exists(os.path.join(scene_dir, 'frame-{:06d}.rendered_normals.png'.format(n-1)))
        if depth_done and (normals_done or not args.save_normals):
            print 'Skipping scene', scenename, 'as it is already rendered'
            continue

        print('[{}/{}] Rendering {}'.format(scene_num+1, len(scene_dirs), scenename))

        # load and display the model
        tri = LoadPly(os.path.join(scene_dir, '{}_vh_clean_2.ply'.format(scenename)), autoScale=False)
        viewer.addModel(tri)
        
        for i in tqdm.tqdm(range(1,n+1)):
            pose = np.loadtxt(os.path.join(scene_dir, 'frame-{:06d}.pose.txt'.format(i-1)))
            tri.setModelM(np.linalg.inv(pose))
            
            viewer.redraw()

            rgba, xyzw = viewer.capture()

            depth = (xyzw[:, :, 3] * 1000.0).astype(np.uint16)
            depth_file = os.path.join(scene_dir, 'frame-{:06d}.rendered_depth.png'.format(i-1))
            cv2.imwrite(depth_file, depth)

            if args.save_normals:
                bgr = (rgba[:, :, 2::-1] * np.iinfo(np.uint16).max).astype(np.uint16)
                bgr_file = os.path.join(scene_dir, 'frame-{:06d}.rendered_normal.png'.format(i-1))
                cv2.imwrite(bgr_file, bgr)

        viewer.removeAll()
    viewer.stop()
