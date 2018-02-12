"""
Compare learned and fixed operators.
"""
import sys, os, datetime
import pickle as pkl
sys.path.insert(0, '../../')
from learned_operators import *
from fixed_operators import *
from utils import *
from model_params import ModelParams
from dataset import Dataset
import argparse

# Available datasets: mnist, mnist_noise_variation_*, mnist_rand_bg, mnist_bg_rot, convex, rect, rect_images
# Example command: 
# python compare_operators.py toep_rect toeplitz_like rect 1_27_18 1 1 5 1e-3 0.9 0 downsample
parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("fn")
parser.add_argument("dataset")
parser.add_argument("result_dir")
parser.add_argument("r", type=int)
parser.add_argument("learn_corner", type=int)
parser.add_argument("n_diag_learned", type=int)
parser.add_argument('lr', type=float)
parser.add_argument('mom', type=float)
parser.add_argument('test', type=int)
parser.add_argument('transform')
parser.add_argument('layer_size', type=int)
args = parser.parse_args()


input_size = 784
if args.dataset == 'cifar10':
	input_size = 3072
	if args.transform == 'grayscale':
		input_size = 1024
	elif args.transform == 'downsample':
		input_size = 768
print input_size
num_layers = 1
out_dir = '/dfs/scratch1/thomasat/'
loss = 'cross_entropy'
steps = 50000
batch_size = 50
layer_size = args.layer_size
if args.transform in ['cnn', 'grayscale']:
	layer_size = 1024
test_size = 1000
check_disp = False
fix_G = False
init_type = 'toeplitz'
init_stddev = 0.1 # For random initialization
test_freq = 100
checkpoint_freq = 1000
n_trials = 5
log_path = os.path.join(out_dir, 'tensorboard', args.result_dir)
results_dir = os.path.join(out_dir, 'results', args.result_dir) 
checkpoint_path = os.path.join(out_dir, 'checkpoints', args.result_dir)

print log_path, results_dir, checkpoint_path

#Available test_fns: [low_rank, toeplitz_like, hankel_like, vandermonde_like, unconstrained, circulant_sparsity]
fn = locals()[args.fn]  
dataset = Dataset(args.dataset, input_size, steps, args.transform, test_size, args.test)

out_size = dataset.out_size() # 10 for MNIST, 2 for convex, rect, rect_images


# Current Toeplitz-like is a special case: inversion assumes Sylvester type displacement
disp_type = 'stein'
if fn.__name__ == 'toeplitz_like':
	disp_type = 'sylvester'

params = ModelParams(args.dataset, args.transform, args.test, log_path, input_size, layer_size, out_size, num_layers, loss, args.r, steps, batch_size, 
		args.lr, args.mom, init_type, fn.__name__, disp_type, args.learn_corner, args.n_diag_learned, 
		init_stddev, fix_G, check_disp, checkpoint_freq, checkpoint_path)

print 'Params:\n', params

# Save params + git commit ID
this_results_dir = params.save(results_dir, args.name)

for test_iter in range(n_trials):
	this_iter_name = fn.__name__ + str(test_iter)
	params.log_path = os.path.join(log_path, args.name + '_' + str(test_iter))
	params.checkpoint_path = os.path.join(checkpoint_path, args.name + '_' + str(test_iter))

	print 'Tensorboard log path: ', params.log_path
	print 'Tensorboard checkpoint path: ', params.checkpoint_path

	losses, accuracies = fn(dataset, params, test_freq)
	tf.reset_default_graph()

	out_loc = os.path.join(this_results_dir, this_iter_name)
	pkl.dump(losses, open(out_loc + '_losses.p', 'wb'))
	pkl.dump(accuracies, open(out_loc + '_accuracies.p', 'wb'))

	print 'Saved losses and accuracies for ' + fn.__name__ + ' to: ' + out_loc

