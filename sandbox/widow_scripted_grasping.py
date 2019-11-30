import roboverse
import numpy as np
import time
import roboverse.utils as utils
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--save_video", action="store_true")
args = parser.parse_args()

env = roboverse.make('WidowGraspOne-v0', gui=True)
obj_key = 'lego'
num_grasps = 0

env.reset()
# target_pos += np.random.uniform(low=-0.05, high=0.05, size=(3,))
images = []

print(env.get_end_effector_pos())

episode_reward = 0.
holding = False

for i in range(1000):
    ee_pos = env.get_end_effector_pos()
    object_pos = env.get_object_midpoint(obj_key)

    xyz_diff = object_pos - ee_pos
    xy_diff = xyz_diff[:2]
    xy_goal_diff = (env._goal_pos - object_pos)[:2]

    if np.linalg.norm(xyz_diff) > 0.042 and not holding:
        action = object_pos - ee_pos
        action *= 3.0
        grip=0.
        print('Approaching')
    elif o[3] > 0.05 and not holding:
        # o[3] is gripper tip distance
        action = np.zeros((3,))
        grip=0.8
        print('Grasping')
    elif np.linalg.norm(xy_goal_diff) > 0.02 and not holding:
        action = env._goal_pos - object_pos
        grip=1.
        action *= 3.0
        action[2] /= 10
        print('Moving')
    elif info['object_goal_distance'] > 0.01 and not holding:
        action = env._goal_pos - object_pos
        grip = 1.
        action *= 3.0
        print('Lifting')
    elif np.linalg.norm((env.get_object_midpoint('bowl') - object_pos)[:2]) > 0.02:
        action = env.get_object_midpoint('bowl') - object_pos
        grip = 1.
        action *= 1.0
        action[2] = 0
        print("Moving to Bowl")
        holding = True
    else:
        action = np.zeros((3,))
        grip=0.
        holding = True
        print('Dropping')


    

    action = np.append(action, [grip])

    if args.save_video:
        img = env.render()
        images.append(img)

    time.sleep(0.05)
    o, r, d, info = env.step(action)
    print(action)
    print(o[3])
    print(r)
    print('object to goal: {}'.format(info['object_goal_distance']))
    print('object to gripper: {}'.format(info['object_gripper_distance']))
    episode_reward += r

print('Episode reward: {}'.format(episode_reward))
object_pos = env.get_object_midpoint(obj_key)
if object_pos[2] > -0.1:
    num_grasps += 1

if args.save_video:
    utils.save_video('data/lego_test_{}.avi'.format(0), images)