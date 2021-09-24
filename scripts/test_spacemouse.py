import roboverse as rv
import numpy as np
import pickle as pkl
from tqdm import tqdm
from roboverse.utils.renderer import EnvRenderer, InsertImageEnv
from roboverse.bullet.misc import quat_to_deg 
import os
from PIL import Image
import argparse
images = []
spacemouse = rv.devices.SpaceMouse(DoF=3)


env = rv.make('SawyerRigMultiobj-v0', test_env=True, object_subset=['grill_trash_can'], gui=True)
for j in range(50):
	env.reset()

	for i in range(50):
		img = Image.fromarray(np.uint8(env.render_obs()))
		images.append(img)
		action = spacemouse.get_action()
		next_observation, reward, done, info = env.step(action)