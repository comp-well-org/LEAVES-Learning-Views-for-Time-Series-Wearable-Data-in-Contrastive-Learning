from random import random
import numpy as np
import pandas as pd
import os
from torch.utils.data import Dataset
from utils.data_utils import normalize_data, Catergorical2OneHotCoding
from utils import augmentation as aug
import random


class TransDataset(Dataset):
    def __init__(self, filename, data_normalization=True, is_training=True, augmentation=False):
        super(TransDataset).__init__()
        self.is_training = is_training
        self.augmentation = augmentation
        
        # first, check whether or not the file exist
        # filename_data must not be none.
        if not os.path.isfile(filename):
            print(filename + "doesn't exist!\n")
            exit(0)
        # then load the data.
        if filename.split('.')[-1] == "csv":
            data = pd.read_csv(filename, sep='\t', header=None).values
            self.data_y = data[:, 0]
            self.data_x = data[:, 1:]
            self.data_y = Catergorical2OneHotCoding(self.data_y.astype(np.int8))
        else:
            data_dict = np.load(filename, allow_pickle=True).item();
            self.data_x = data_dict['ECG_signal']
            self.data_x = np.transpose(self.data_x, (0,2,1))
            self.data_y = data_dict['label']
            self.data_y = Catergorical2OneHotCoding(self.data_y.astype(np.int8).reshape(-1,))

        if data_normalization:
            std_ = self.data_x.std(axis=1, keepdims=True)
            std_[std_ == 0] = 1.0
            self.data_x = (self.data_x - self.data_x.mean(axis=1, keepdims=True)) / std_
        if len(self.data_x) == 1:
            self.data_x = np.expand_dims(self.data_x, axis=-1)

    def __len__(self):
        return self.data_x.shape[0]

    def normalization(self, x):
        # x = x.reshape((1,-1))
        x = (x - np.min(x, axis=1, keepdims=True))/(np.max(x, axis=1, keepdims=True) - np.min(x, axis=1, keepdims=True) + 0.00000001)
        return x
    
    def transformation(self, x):
        if self.augmentation:
            args = random.choice(['jitter', 'scaling', 'permutation', 'rotation', 'magnitudewarp', 'timewarp', 'windowslice', 'windowwarp'])
        else:
            args = 'original'
            
        if args == 'jitter':
            x = aug.jitter(x)
        elif args == 'scaling':
            x = aug.scaling(x)
        elif args == 'permutation':
            x = aug.permutation(x)
        elif args == 'rotation':
            x = aug.rotation(x)
        elif args == 'magwarp':
            x = aug.magnitude_warp(x)
        elif args == 'timewarp':
            x = aug.time_warp(x)
        elif args == 'windowslice':
            x = aug.window_slice(x)
        elif args == 'windowwarp':
            x = aug.window_warp(x)
        else:
            pass;
        x = self.normalization(x)
        return x
    
    def __getitem__(self, index):
        x =  self.data_x[index]
        y =  self.data_y[index]
        self.is_training = False
        if self.is_training:
            x1 = self.transformation(x)
            x2 = self.transformation(x)
            return x1, x2, y
        else:
            x = self.normalization(x)
            # return x, y
            return x, x.copy(), y


def test():
    # something need to be test here.
    print("Test a function!")

if __name__ == "__main__":
    test()
    print("Everything passed")