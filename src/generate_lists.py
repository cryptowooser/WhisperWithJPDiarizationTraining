import os
import numpy as np

def write_list_to_file(file_list, file_path):
    with open(file_path, 'w') as f:
        for item in file_list:
            f.write("%s\n" % item)

def generate_lists(all_wavs_path, list_dir_path):
    # Create list_dir_path if it doesn't exist
    os.makedirs(list_dir_path, exist_ok=True)

    # Get list of all WAV files
    all_files = [f.replace('.wav', '') for f in os.listdir(all_wavs_path) if f.endswith('.wav')]

    # Shuffle the files to ensure randomness
    np.random.shuffle(all_files)

    # Define the number of files
    num_files = len(all_files)

    # Split the files into train, dev, and test sets based on the 70/15/15 split
    train_files = all_files[:int(num_files*0.7)]
    dev_files = all_files[int(num_files*0.7):int(num_files*0.85)]
    test_files = all_files[int(num_files*0.85):]

    # Write the full lists to files
    write_list_to_file(train_files, os.path.join(list_dir_path, 'train.full.txt'))
    write_list_to_file(dev_files, os.path.join(list_dir_path, 'dev.full.txt'))
    write_list_to_file(test_files, os.path.join(list_dir_path, 'test.full.txt'))

    # Create a mini list based on 10% of the full list
    mini_files = all_files[:int(num_files*0.1)]
    mini_train_files = mini_files[:int(len(mini_files)*0.7)]
    mini_dev_files = mini_files[int(len(mini_files)*0.7):int(len(mini_files)*0.85)]
    mini_test_files = mini_files[int(len(mini_files)*0.85):]

    # Write the mini lists to files
    write_list_to_file(mini_train_files, os.path.join(list_dir_path, 'train.mini.txt'))
    write_list_to_file(mini_dev_files, os.path.join(list_dir_path, 'dev.mini.txt'))
    write_list_to_file(mini_test_files, os.path.join(list_dir_path, 'test.mini.txt'))
