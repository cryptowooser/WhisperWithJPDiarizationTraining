import argparse
import yaml
from src.generate_rttms import generate_rttms
from src.generate_audio_files import generate_cleaned_audio_files
from src.generate_uems import generate_uems

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def main(config_path):
    # Load configuration
    config = load_config(config_path)
    
    # Access configuration variables
    # For example: batch_size = config['batch_size']
    print(config['data_preparation']['video_audio_files_location'])

    generate_cleaned_audio_files(config['data_preparation']['video_audio_files_location'], config['data_preparation']['processed_files_folder'])    
    generate_rttms(config['data_preparation']['aegisub_scripts_location'], config['data_preparation']['processed_files_folder'], config['data_preparation']['acceptable_styles_location'])
    generate_uems(config['data_preparation']['processed_files_folder'], config['data_preparation']['uem_settings']['start_time'], config['data_preparation']['uem_settings']['end_time'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Speech Segmentation Training")
    parser.add_argument("--config", default="config.yaml", help="Path to the configuration file")
    args = parser.parse_args()
    
    main(args.config)

