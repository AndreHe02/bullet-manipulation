import roboverse
import numpy as np
import pickle as pkl
from tqdm import tqdm
import os
from PIL import Image
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("--name", type=str)
parser.add_argument("--num_trajectories", type=int, default=1000)
parser.add_argument("--num_timesteps", type=int, default=75)
parser.add_argument("--video_save_frequency", type=int,
                    default=0, help="Set to zero for no video saving")
parser.add_argument("--gui", dest="gui", action="store_true", default=False)

args = parser.parse_args()
data_save_path = "/home/ashvin/data/s3doodad/sasha/demos/" + args.name + ".pkl"
video_save_path = "/home/ashvin/data/s3doodad/sasha/demos/videos/" + args.name

num_objects = 2

env = roboverse.make('SawyerMultiobjGrasp-v0',
    gui=args.gui,
    num_objects=num_objects,
    # object_ids = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29], # [0, 1, 25, 30, 50, 215, 255, 265, 300, 310],
    object_ids = [0, 1, 25, 30, 50, 215, 255, 265, 300, 310],
    obs_img_dim=96,
)
object_name = 'lego'
num_grasps = 0
image_data = []

obs_dim = env.observation_space.shape
assert(len(obs_dim) == 1)
obs_dim = obs_dim[0]
act_dim = env.action_space.shape[0]

if not os.path.exists(video_save_path) and args.video_save_frequency > 0:
    os.makedirs(video_save_path)


imlength = env.obs_img_dim * env.obs_img_dim * 3

dataset = []

for i in tqdm(range(args.num_trajectories)):
    # if i % 2 == 0:
    #     noise = 1
    # else:
    #     noise = 0.1
    # trajectory = {
    #     'image_observations': np.zeros((args.num_timesteps, imlength), dtype=np.uint8),
    #     'observations': np.zeros((args.num_timesteps, obs_dim), dtype=np.float),
    #     'next_observations': np.zeros((args.num_timesteps, obs_dim), dtype=np.float),
    #     'actions': np.zeros((args.num_timesteps, act_dim), dtype=np.float),
    #     'rewards': np.zeros((args.num_timesteps), dtype=np.float),
    #     'terminals': np.zeros((args.num_timesteps), dtype=np.uint8),
    #     'agent_infos': np.zeros((args.num_timesteps), dtype=np.uint8),
    #     'env_infos': np.zeros((args.num_timesteps), dtype=np.uint8),
    # }

    trajectory = {
        'observations': np.zeros((args.num_timesteps, imlength), dtype=np.uint8),
        'next_observations': np.zeros((args.num_timesteps, imlength), dtype=np.uint8),
        'actions': np.zeros((args.num_timesteps, act_dim), dtype=np.float),
        'rewards': np.zeros((args.num_timesteps), dtype=np.float),
        'terminals': np.zeros((args.num_timesteps), dtype=np.uint8),
        'agent_infos': np.zeros((args.num_timesteps), dtype=np.uint8),
        'env_infos': np.zeros((args.num_timesteps), dtype=np.uint8),
    }


    env.reset()
    object_name = random.randint(0, num_objects-1)
    target_pos = env.get_object_midpoint(object_name)
    images = []
    for j in range(args.num_timesteps):
        img = np.uint8(env.render_obs())
        images.append(Image.fromarray(img))
        trajectory['observations'][j, :] = img.transpose().flatten()

        ee_pos = env.get_end_effector_pos()

        if j < 25:
            action = target_pos - ee_pos
            action[2] = 0.
            action *= 3.0
            grip = 0.
        elif j < 35:
            action = target_pos - ee_pos
            action[2] -= 0.03
            action *= 3.0
            action[2] *= 2.0
            grip = 0.
        elif j < 42:
            action = np.zeros((3,))
            grip = 0.5
        else:
            action = np.zeros((3,))
            action[2] = 1.0
            action = np.random.normal(action, 0.25)
            grip = 1.

        action = np.append(action, [grip])
        action = np.random.normal(action, 0.1)

        next_observation, reward, done, info = env.step(action)


        trajectory['actions'][j, :] = action
        trajectory['next_observations'][j, :] = np.uint8(env.render_obs()).transpose().flatten()
        trajectory['rewards'][j] = reward

    object_pos = env.get_object_midpoint(object_name)
    if object_pos[2] > -0.35:
        num_grasps += 1

    if args.video_save_frequency > 0 and i % args.video_save_frequency == 0:
        images[0].save('{}/{}.gif'.format(video_save_path, i),
                       format='GIF', append_images=images[1:],
                       save_all=True, duration=100, loop=0)

    dataset.append(trajectory)

print('Success Rate: {}'.format(num_grasps / args.num_trajectories))
file = open(data_save_path, 'wb')
pkl.dump(dataset, file)
file.close()

