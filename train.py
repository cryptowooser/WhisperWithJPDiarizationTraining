import argparse
import yaml
import os
from src.generate_rttms import generate_rttms
from src.generate_audio_files import generate_cleaned_audio_files
from src.generate_uems import generate_uems
from src.generate_lists import generate_lists
def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def generate_database_yml(config):
    # First, read the template file
    with open('default_files/database_template.yml', 'r') as f:
        template = f.read()

    # Convert backslashes to forward slashes and ensure consistent formatting. Needed because otherwise the paths are not recognized.
    def path_to_posix(path):
        return path.replace('\\', '/').replace('//', '/')

    # Then format it with your directory paths
    formatted_config = template.format(
        wav_dir=path_to_posix(os.path.join(config['data_preparation']['processed_files_folder'], 'prepped_audio')),
        rttm_dir=path_to_posix(os.path.join(config['data_preparation']['processed_files_folder'], 'rttm_files')),
        uem_dir=path_to_posix(os.path.join(config['data_preparation']['processed_files_folder'], 'uems')),
        lists_dir=path_to_posix(os.path.join(config['data_preparation']['processed_files_folder'], 'lists')),
        uri="{uri}"
    )

    # Write the formatted config to a new file
    with open('database.yml', 'w') as f:
        f.write(formatted_config)


def main(config_path):
    # Load configuration
    config = load_config(config_path)
    
    # Access configuration variables
    # For example: batch_size = config['batch_size']
    print(config['data_preparation']['video_audio_files_location'])

    generate_cleaned_audio_files(config['data_preparation']['video_audio_files_location'], config['data_preparation']['processed_files_folder'])    
    generate_rttms(config['data_preparation']['aegisub_scripts_location'], config['data_preparation']['processed_files_folder'], config['data_preparation']['acceptable_styles_location'])
    generate_uems(config['data_preparation']['processed_files_folder'], config['data_preparation']['uem_settings']['start_time'], config['data_preparation']['uem_settings']['end_time'])
    #Generate database.yml file
    generate_database_yml(config)

    processed_audio_folder = os.path.join(config['data_preparation']['processed_files_folder'], 'prepped_audio')
    lists_folder = os.path.join(config['data_preparation']['processed_files_folder'], 'lists')
    rttms_folder = os.path.join(config['data_preparation']['processed_files_folder'], 'rttm_files')
    uems_folder = os.path.join(config['data_preparation']['processed_files_folder'], 'uems')

    generate_lists(processed_audio_folder, lists_folder)

    #TODO Integrate trainer logic here


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Speech Segmentation Training")
    parser.add_argument("--config", default="config.yaml", help="Path to the configuration file")
    args = parser.parse_args()
    
    main(args.config)
