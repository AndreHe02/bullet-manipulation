import numpy as np
import pdb 
import pybullet as p
import roboverse
import roboverse.bullet as bullet
import math
from roboverse.bullet.misc import load_urdf, load_obj, load_random_objects
import os
# connect to the VR server (by p.SHARED_MEMORY)
bullet.connect()
bullet.setup()

# query event which is a tuple of changes in controller. Index corresponds to POSITION, ORIENTATION, BUTTTON etc
POSITION = 1
ORIENTATION = 2
ANALOG = 3
BUTTONS = 6

# set the environment
env = roboverse.make('SawyerGraspOne-v0', render=True)

controllers = [e[0] for e in p.getVREvents()]

trigger = 0

num_grasps = 0
save_video = True
curr_dir = os.path.dirname(os.path.abspath(__file__))
home_dir = os.path.dirname(curr_dir)
pklPath = home_dir + '/data'
trajectories = []
image_data = []
num_of_sample = 5

ORIENTATION_ENABLED = True

data = []

for i in range(num_of_sample): # number of runs for human to demonstrate
    o = env.reset()
    target_pos = env.get_object_midpoint('duck')
    target_pos += np.random.uniform(low=-0.05, high=0.05, size=(3,))
    images = []

    traj = dict(
        observations=[o],
        actions=[],
        rewards=[],
        next_observations=[],
        terminals=[],
        agent_infos=[],
        env_infos=[],
    )

    accept = True
    start = False
    while True:

        ee_pos = env.get_end_effector_pos()

        traj["observations"].append(env.get_observation())

        events = p.getVREvents()

        if events:
            e = events[0]
        else:
            continue

        if e[BUTTONS][32] & p.VR_BUTTON_WAS_TRIGGERED:
            accept = False
            break

        if e[BUTTONS][2] & p.VR_BUTTON_WAS_TRIGGERED:
            accept = False
            break

        # Detect change in button, and change trigger state
        if e[BUTTONS][33] & p.VR_BUTTON_WAS_TRIGGERED:
            trigger = 1
        if e[BUTTONS][33] & p.VR_BUTTON_WAS_RELEASED:
            trigger = 0

        if e[0] != controllers[0]:
            break

        # pass controller position and orientation into the environment
        cont_pos = e[POSITION]
        cont_orient = bullet.deg_to_quat([180, 0, 0])
        if ORIENTATION_ENABLED:
            cont_orient = e[ORIENTATION]
            cont_orient = list(cont_orient)
            #cont_orient = bullet.quat_to_deg(cont_orient)
            #cont_orient = list(cont_orient)
            #cont_orient[0] = 180 + cont_orient[0]
            #cont_orient[1] = 180 + cont_orient[1]
            #cont_orient = bullet.deg_to_quat(cont_orient)

        action = [cont_pos[0] - ee_pos[0], cont_pos[1] - ee_pos[1], cont_pos[2] - ee_pos[2]]
        grip = trigger

        action = np.append(action, [grip])
        action = np.append(action, cont_orient)

        img = env.render()
        images.append(np.uint8(img))

        # action is now delta_position, grip (boolean) and orientation
        next_state, reward, done, info = env.step(action)
        print(next_state, reward, done, info)
        traj["next_observations"].append(next_state)
        traj["actions"].append(action)
        traj["rewards"].append(reward)
        traj["terminals"].append(done)
        traj["agent_infos"].append(info)
        traj["env_infos"].append(info)

        object_pos = env.get_object_midpoint('duck')

        if object_pos[2] > -0.1 + 0.3:
            num_grasps += 1
            break

    if accept:
        print("accept trajectory")
        print(traj)
        data.append(traj)
    else:
        print(traj)
        print("discarded trajectory")

path = "~/vr_demos.npy"
np.save(path, data)

#print('Num attempts: {}'.format(j))
print('Num grasps: {}'.format(num_grasps))
