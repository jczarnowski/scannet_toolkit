import sys
sys.path.insert(0,'./PyGLer/src')
sys.path.insert(0,'./PyGLer/src/pygler/gui')

from utils import ComputeNormals
from pygler.utils import CreateAxisModel, CreateCubeModel

import cv2
import glob

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

if __name__ == '__main__':
    if ((len(sys.argv) < 4 or < len(sys.argv > 4)):
        print("python main.py scenes_list scannet_dir output_dir")
    scenes = []
    with open('{}'.format(sys.argv[1])) as f:
        scenes = [line.rstrip() for line in f.readlines()]

    viewer = PyGLer(useFBO=True)
    viewer.start()
    for scenename in scenes:
        print('Running ',scenename)
        tri = PyGLerModel.LoadPly("{0}/scans/{1}/{1}_vh_clean_2.ply".format(sys.argv[2],scenename),autoScale=False)

        viewer.addModel(tri)
        
        n = len(glob.glob('{}/exported/{}/*.color.jpg'.format(sys.argv[2],scenename)))
        for i in range(0,n):
            pose = np.loadtxt('{}/exported/{}/frame-{:06d}.pose.txt'.format(sys.argv[2],scenename,i))
            
            tri.setModelM(np.linalg.inv(pose))
            
            depth,bgr = viewer.Convert2BGRD(viewer.capture())
            bgr = cv2.resize(bgr,(256,192),interpolation=cv2.INTER_NEAREST)
            depth = cv2.resize(depth,(256,192),interpolation=cv2.INTER_NEAREST)
            np.save('{}/{}/rendered_normal_{:06d}.npy'.format(sys.argv[3],scenename,i),bgr.astype(np.float32))
            np.save('{}/{}/rendered_depth_{:06d}.npy'.format(sys.argv[3],scenename,i),depth)
            viewer.redraw()
            
viewer.removeModel(tri)
