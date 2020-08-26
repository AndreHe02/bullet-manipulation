import roboverse
import numpy as np
#import skvideo.io
import os
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from PIL import Image
import sys
import numpy as np
import pdb 
import pybullet as p
import roboverse
import roboverse.bullet as bullet
import math
from roboverse.bullet.misc import load_urdf, load_obj
import os

from tqdm import tqdm
from PIL import Image
import argparse
import time

fig = plt.figure()

data = np.load(sys.argv[1], allow_pickle=True)

success = []
failed_id = []

reward_type = 'sparse'
env = roboverse.make('Widow200GraspV6ThirtyRandObj-v0', reward_type=reward_type,
                     randomize=True, observation_mode='pixels_debug', num_objects=2)

for i in tqdm(range(len(data))):

    ax = plt.axes(projection='3d')
    traj = data[i]

    object_positions = traj["original_object_positions"]
    env.object_positions = object_positions
    env.randomize = False

    object_names_idx = traj["object_names_idx"]
    print("object_names_idx: ", object_names_idx)
    env.deterministic_idx = object_names_idx

    observations = np.array([traj["observations"][j][env.fc_input_key] for j in range(len(traj["observations"]))])
    ax.plot3D(observations[:, 0], observations[:, 1], observations[:, 2], label="original trajs", color="red")

    actions = traj["actions"]
    first_observation = traj["observations"][0]

    env.reset()
    print("object positions after reset: ")
    print(env.object_positions)
    images = []

    object_info = env.get_obj_obs_array()

    all_obj_pos = []
    for k in range(2):
        all_obj_pos.append(object_info[7*k:7*k+3])
    all_obj_pos = np.array(all_obj_pos)
    print("all_obj_pos: ", all_obj_pos)
    ax.scatter3D(all_obj_pos[:,0], all_obj_pos[:,1], all_obj_pos[:,2], label="actual position")

    replay_obs_list = []
    obs = env.get_observation()

    replay_obs_list.append(obs[env.fc_input_key])
    #data[i]["observations"] = data[i]["observations"][1:]

    print("length of obs: ", len(data[i]["observations"]))
    print("length of action: ", len(data[i]["actions"]))

    for index in range(len(actions)):
        data[i]["observations"][index] = obs
        a = actions[index]
        obs, rew, done, info = env.step(a)
        data[i]["next_observations"][index] = obs
        replay_obs_list.append(obs[env.fc_input_key])
        images.append(Image.fromarray(env.render_obs()))

    print(info["grasp_success"])
    success.append(info["grasp_success"])

    if not info["grasp_success"]:
        failed_id.append(i)

    replay_obs_list = np.array(replay_obs_list)
    ax.plot3D(replay_obs_list[:, 0], replay_obs_list[:, 1], replay_obs_list[:, 2], label="replay", color="blue")

    if not os.path.exists('replay_videos_single_random'):
        os.mkdir('replay_videos_single_random')

    images[0].save('{}/{}.gif'.format("replay_videos_single_random", i),
                format='GIF', append_images=images[1:],
                save_all=True, duration=100, loop=0)
    plt.legend()
    fig.savefig('{}/{}.png'.format("replay_videos_single_random", i))
    fig.clf()
    
success = np.array(success)
print("mean: ", success.mean())
print("std: ", success.std())
print("all success: ", (success == 1).all())
print("failed id: ")
print(failed_id)

path = "{}_replayed.npy".format(sys.argv[1][:-4])
np.save(path, data)