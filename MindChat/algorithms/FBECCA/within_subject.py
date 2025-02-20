import os
import numpy as np
from sklearn.pipeline import clone
import csv
import pickle
from sklearn.model_selection import StratifiedKFold
# from bin.base import generate_cca_references, generate_filterbank
# from bin.FBECCA import FBECCA
from metabci.brainda.algorithms.decomposition import (
    FBSCCA, FBECCA, FBDSP, FBTRCA,
    generate_filterbank, generate_cca_references)
from bin.tools import preprocess
from bin.online_FBECCA import OnlineFBECCA
from SSVEP_Calibration.cfg import *

config = {
    'dataset_path': r'~\MindChat\data/',
    'train_files': ['s1_40class.mat',],
    'test_files': ['s1_40class.mat'],
    'kfold': 6,
    'data_dur': (0, 1.5),
    'win_dur': (0.2, 1.5),
    'fs': 1200,
    'resample': 5,
    'channels': [c - 1 for c in [1, 2, 3, 4, 5, 6, 7, 8, 9,]],
    'n_bands': 3,
    'n_harmonics': 3,
    # the order should be in consistent with the label order
    'freqs': [freq for freq in TYPE_FREQ_TABLE.values()], #sorted([freq for freq in TYPE_FREQ_TABLE.values()], key=str),
    'model': 'FBECCA',
    'save': True,
}

subjects = []
val_acc_subjects, test_acc_subjects = [], []
for dir in sorted(os.listdir(config['dataset_path'])):
    files = set(os.listdir(config['dataset_path'] + dir))
    if not set(config['train_files'] + config['test_files']).issubset(files):
        continue
    print(f'Training on subject {dir}')
    subjects.append(dir)

    subject_path = config['dataset_path'] + dir + '/'
    total_train_x, total_train_y = [], []
    for file in config['train_files']:
        x, y = preprocess(subject_path + file, config)
        total_train_x.append(x), total_train_y.append(y)

    Yf = generate_cca_references(config['freqs'], config['fs']//config['resample'], config['win_dur'][1] - config['win_dur'][0],
                                 phases=None, n_harmonics=config['n_harmonics'])

    wp = [[config['freqs'][0] * i, 48] for i in range(1, config['n_bands'] + 1)]
    ws = [[config['freqs'][0] * i - 2, 50] for i in range(1, config['n_bands'] + 1)]
    # todo: usually be affected by power-line noise
    filterbank = generate_filterbank(wp, ws, config['fs']//config['resample'], order=4, rp=1)
    filterweights = np.arange(1, len(filterbank) + 1) ** (-1.25) + 0.25
    # model = FBECCA(filterbank, filterweights=filterweights, n_jobs=8)
    model = eval(f'{config["model"]}(filterbank, filterweights=filterweights, n_jobs=8)')

    val_acc = []
    skfSplitter = [StratifiedKFold(config['kfold']).split(total_train_x[i], total_train_y[i]) for i in range(len(total_train_x))]
    for i in range(config['kfold']):
        train_x, train_y, val_x, val_y = [], [], [], []
        for x, y, skf in zip(total_train_x, total_train_y, skfSplitter):
            train_idxes, val_idxes = next(skf)
            train_x.append(x[train_idxes]), train_y.append(y[train_idxes])
            val_x.append(x[val_idxes]), val_y.append(y[val_idxes])
        train_x, train_y = np.concatenate(train_x), np.concatenate(train_y)
        val_x, val_y = np.concatenate(val_x), np.concatenate(val_y)

        model = clone(model).fit(train_x, train_y, Yf=Yf)
        pred_labels = model.predict(val_x)
        val_acc.append(np.mean(val_y == pred_labels))
    val_acc_subjects.append(np.mean(val_acc))

    total_train_x = np.concatenate(total_train_x)
    total_train_y = np.concatenate(total_train_y)
    model = clone(model).fit(total_train_x, total_train_y, Yf=Yf)

    total_test_x, total_test_y = [], []
    for file in config['test_files']:
        x, y = preprocess(subject_path + file, config)
        total_test_x.append(x), total_test_y.append(y)
    total_test_x = np.concatenate(total_test_x)
    total_test_y = np.concatenate(total_test_y)
    pred_labels = model.predict(total_test_x)
    test_acc_subjects.append(np.mean(total_test_y == pred_labels))
    # test_acc_subjects.append(0)

    print(f'subject:{dir}   val acc:{val_acc_subjects[-1]:.4f}  test acc:{test_acc_subjects[-1]:.4f}\n')

    if config['save']:
        file = f"{dir}_FBECCA_{config['train_files'][0].split('.')[0]}_{int(config['win_dur'][1] - config['win_dur'][0])}s.pkl"
        online_model = OnlineFBECCA(config, model)
        with open(f'{subject_path}{file}', 'wb') as f:
            pickle.dump([online_model], f)

with open(f'{config["model"]}_{config["data_dur"][1]}s.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['subject', 'val_acc', 'test_acc'])
    for subject, val_acc, test_acc in zip(subjects, val_acc_subjects, test_acc_subjects):
        writer.writerow([subject, f'{val_acc:.4f}', f'{test_acc:.4f}'])
    val_acc_avg = sum(val_acc_subjects) / len(val_acc_subjects)
    test_acc_avg = sum(test_acc_subjects) / len(test_acc_subjects)
    writer.writerow(['Avg', f'{val_acc_avg:.4f}', f'{test_acc_avg:.4f}'])
print(f"Subjects' val set average acc: {val_acc_avg:.4f}")
print(f"Subjects' test set average acc: {test_acc_avg:.4f}")