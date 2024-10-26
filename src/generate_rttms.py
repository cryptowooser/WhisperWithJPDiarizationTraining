import os 

def generate_rttms(ass_directory_path, output_directory_path, acceptable_styles_path):
    # List all .ass files in the directory
    ass_files = [f for f in os.listdir(ass_directory_path) if f.endswith('.ass')]

    # Initialize a list to store the pairs of .ass and .avi file names
    file_pairs = []

    # Loop through the .ass files
    for ass_file in ass_files:
        # Open the file and read the lines
        with open(os.path.join(ass_directory_path, ass_file), "r", encoding='utf-8') as file:
            lines = file.readlines()

        # Loop through the lines
        for line in lines:
            # Check if the line starts with "Video File:"
            if line.startswith("Video File:"):
                # Extract the .avi file name
                avi_file = line.split('Video File:')[1].strip().split('/')[-1]
                
                # Add the pair of .ass and .avi file names to the list
                file_pairs.append((ass_file, avi_file))
                
                # Stop searching this file, as we've found the .avi file name
                break

    for ass_file, avi_file in file_pairs:
        #The audio file is the avi without the extension
        audio_file = avi_file.replace(".avi","")
        rttm_lines = convert_ass_to_rttm(os.path.join(ass_directory_path, ass_file), audio_file, acceptable_styles_path)
        # First, create the rttm_files subdirectory if it doesn't exist
        rttm_folder = os.path.join(output_directory_path, "rttm_files")
        os.makedirs(rttm_folder, exist_ok=True)  # This creates the folder if it doesn't exist

        # Then write to a file in that subdirectory
        with open(os.path.join(rttm_folder, audio_file + ".rttm"), 'w', encoding='utf-8') as file:
            file.write('\n'.join(rttm_lines))




def time_to_seconds(time_str):
    """
    Converts a time string in the format hours:minutes:seconds.centiseconds to seconds.
    """
    hours, minutes, seconds_centiseconds = time_str.split(":")
    seconds, centiseconds = seconds_centiseconds.split(".")
    
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(centiseconds) / 100
    
    return total_seconds

def convert_ass_to_rttm(file_path, audio_file, acceptable_styles_path):
    # Extract the file_id from the file name
    file_id = file_path.split("/")[-1].replace(".ass", "")
    
    # Initialize a list to store the dialogue data
    dialogue_data = []

    # Open the file and read the lines
    with open(file_path, "r", encoding='utf-8') as file:
        lines = file.readlines()

    with open(acceptable_styles_path, "r", encoding='utf-8') as file:
        acceptable_styles = [line.strip() for line in file.readlines()]
    # Loop through the lines
    for line in lines:
        # Check if the line starts with "Dialogue"
        if line.startswith("Dialogue"):
            # Split the line by comma
            parts = line.split(",")

            # Extract the start time, end time, and speaker name
            start_time = parts[1].strip()
            end_time = parts[2].strip()
            speaker = parts[4].strip()
            style = parts[3].strip()
            # Add the dialogue data to the list
            if style in acceptable_styles:  
                dialogue_data.append((start_time, end_time, speaker))
            
    # Initialize a list to store the RTTM lines
    rttm_lines = []

    # Loop through the dialogue data
    for start_time, end_time, speaker in dialogue_data:
        # Convert the start and end times to seconds
        start_seconds = time_to_seconds(start_time)
        end_seconds = time_to_seconds(end_time)

        # Calculate the duration of the speech segment
        duration = end_seconds - start_seconds

        # Compose the RTTM line
        rttm_line = f"SPEAKER {audio_file} 1 {start_seconds:.2f} {duration:.2f} <NA> <NA> {speaker} <NA> <NA>"

        # Add the RTTM line to the list
        rttm_lines.append(rttm_line)

    return rttm_lines
