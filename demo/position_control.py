import numpy as np
import pdb

import bullet
import devices

space_mouse = devices.SpaceMouse()
space_mouse.start_control()

bullet.connect()
bullet.setup()

## load meshes
sawyer = bullet.load_urdf('sawyer_robot/sawyer_description/urdf/sawyer_xacro.urdf')
table = bullet.load_urdf('table/table.urdf', [.75, -.2, -1], [0, 0, 0.707107, 0.707107], scale=1.0)
duck = bullet.load_urdf('duck_vhacd.urdf', [.75, -.2, 0], [0, 0, 1, 0], scale=0.8)
duck = bullet.load_urdf('lego/lego.urdf', [.75, .2, 0], [0, 0, 1, 0], rgba=[1,0,0,1], scale=1.5)

end_effector = bullet.get_index_by_attribute(sawyer, 'link_name', 'right_l6')
pos = np.array([0.5, 0, 0])
theta = [0.7071,0.7071,0,0]
bullet.position_control(sawyer, end_effector, pos, theta)


while True:

    delta = space_mouse.control
    pos += delta * 0.1
    print(delta, pos)

    bullet.sawyer_ik(sawyer, end_effector, pos, theta, space_mouse.control_gripper)
    bullet.step()
    pos = bullet.get_link_state(sawyer, end_effector, 'pos')

