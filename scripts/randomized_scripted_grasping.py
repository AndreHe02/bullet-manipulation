import roboverse
import numpy as np
from tqdm import tqdm
import pickle
import os
from PIL import Image
import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--video_save_directory", type=str)
parser.add_argument("--data_save_directory", type=str)
parser.add_argument("--num_trajectories", type=int, default=2000)
parser.add_argument("--num_timesteps", type=int, default=50)
parser.add_argument("--video_save_frequency", type=int,
                    default=0, help="Set to zero for no video saving")
parser.add_argument("--gui", dest="gui", action="store_true", default=False)

args = parser.parse_args()
timestamp = roboverse.utils.timestamp()
args.video_save_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'SawyerGrasp', args.video_save_directory + "_" + timestamp)
args.data_save_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'SawyerGrasp', args.data_save_directory)

env = roboverse.make('SawyerGraspOne-v0', gui=args.gui)
object_name = 'lego'
num_grasps = 0
image_data = []

obs_dim = env.observation_space.shape
assert(len(obs_dim) == 1)
obs_dim = obs_dim[0]
act_dim = env.action_space.shape[0]

if not os.path.exists(args.video_save_directory):
    os.makedirs(args.video_save_directory)
if not os.path.exists(args.data_save_directory):
    os.makedirs(args.data_save_directory)

pool = roboverse.utils.DemoPool()

for j in tqdm(range(args.num_trajectories)):
    env.reset()
    target_pos = env.get_object_midpoint(object_name)
    target_pos += np.random.uniform(low=-0.05, high=0.05, size=(3,))
    images = []

    for i in range(args.num_timesteps):
        ee_pos = env.get_end_effector_pos()

        if i < 25:
            action = target_pos - ee_pos
            action[2] = 0.
            action *= 3.0
            grip = 0.
        elif i < 35:
            action = target_pos - ee_pos
            action[2] -= 0.03
            action *= 3.0
            action[2] *= 2.0
            grip = 0.
        elif i < 42:
            action = np.zeros((3,))
            grip = 0.5
        else:
            action = np.zeros((3,))
            action[2] = 1.0
            grip = 1.

        action = np.append(action, [grip])

        if args.video_save_frequency > 0 and j % args.video_save_frequency == 0:
            img = env.render()
            images.append(Image.fromarray(np.uint8(img)))

        observation = env.get_observation()
        next_state, reward, done, info = env.step(action)
        pool.add_sample(observation, action, next_state, reward, done)

    object_pos = env.get_object_midpoint(object_name)
    if object_pos[2] > -0.1:
        num_grasps += 1
        print('Num grasps: {}'.format(num_grasps))

    if args.video_save_frequency > 0 and j % args.video_save_frequency == 0:
        images[0].save('{}/{}.gif'.format(args.video_save_directory, j),
                       format='GIF', append_images=images[1:],
                       save_all=True, duration=100, loop=0)

params = env.get_params()
pool.save(params, args.data_save_directory, '{}_pool_{}.pkl'.format(timestamp, pool.size))