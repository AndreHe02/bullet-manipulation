import pickle
import argparse
import roboverse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data-directory", type=str)
args = parser.parse_args()

data_directory = os.path.join(
    os.path.dirname(__file__), "..", 'data', args.data_directory)
print(data_directory)
keys = ('observations', 'actions', 'next_observations', 'rewards', 'terminals')
fields_all = {}
fields_success_only = {}

timestamp = roboverse.utils.timestamp()

for key in keys:
    fields_all[key] = []
    fields_success_only[key] = []

for root, dirs, files in os.walk(data_directory):
    for f in files:
        if "pool" in f:
            with open(os.path.join(root, f), 'rb') as fp:
                print("fp", fp)
                trajectories = pickle.load(fp)
            if 'success_only' in f:
                for key in keys:
                    fields_success_only[key].extend(trajectories[key])
            else:
                for key in keys:
                    fields_all[key].extend(trajectories[key])

save_all_path = os.path.join(data_directory, 'combined_all_{0}.pkl'.format(timestamp))
with open(save_all_path, 'wb+') as fp:
    pickle.dump(fields_all, fp)
    print('saved to {}'.format(save_all_path))

save_success_only_path = os.path.join(data_directory, 'combined_success_only_{0}.pkl'.format(timestamp))
with open(save_success_only_path, 'wb+') as fp:
    pickle.dump(fields_success_only, fp)
    print('saved to {}'.format(save_success_only_path))

# WidowX Version:
# args.data_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', args.data_directory)
# args.output_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', args.output_directory)

# trajectories = []
# timestamp = roboverse.utils.timestamp()

# for root, dirs, files in os.walk(args.data_directory):
#     for f in files:
#         if "pool" in f:
#             with open(os.path.join(args.data_directory, f), 'rb') as fp:
#                 t = pickle.load(fp)
#             trajectories.extend(t)

# if not os.path.exists(args.output_directory):
#     os.makedirs(args.output_directory)

# with open(os.path.join(args.output_directory, 'data_{0}.pkl'.format(timestamp)), 'wb+') as fp:
#     pickle.dump(trajectories, fp)
