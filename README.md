# structured_matrices
Learning with structured matrices

## Requirements
Python 3.6+

pytorch>=0.4.0

cupy>=4.0.0


## Example Usage
```
python compare.py --name=test --methods=toeplitz_like --dataset=mnist_noise_1 --result_dir=fat --r=1 --lr=1e-2 --decay_rate=1.0 --mom=0.9 --steps=3000 --batch_size=1024 --test=1 --layer_size=784 --torch=1 --model=MLP
```
`tensorboard --logdir=path/to/tensorboard/result_dir`
