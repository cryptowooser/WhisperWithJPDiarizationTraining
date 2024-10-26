import os
import soundfile as sf

def generate_uems(output_directory_path, uem_start_time, uem_end_time):
    # specify the directory containing your WAV files
    wav_dir = os.path.join(output_directory_path, "prepped_audio")
    # specify the directory where you want to store your UEM files
    uem_dir = os.path.join(output_directory_path, "uems")

    # create the UEM directory if it doesn't exist
    os.makedirs(uem_dir, exist_ok=True)

    # loop over each file in the WAV directory
    for filename in os.listdir(wav_dir):
        if filename.endswith('.wav'):
            # read the WAV file to get its duration
            file_path = os.path.join(wav_dir, filename)
            data, samplerate = sf.read(file_path)
            duration = len(data) / samplerate
            
            if duration <= float(uem_start_time) or duration < float(uem_end_time):
                raise Exception("Audio file duration is less than the UEM start or end time.")    # create the corresponding UEM file
            
            # Remove the file extension from the filename
            session_name = os.path.splitext(filename)[0]
            
            uem_filename = filename.replace('.wav', '.uem')
            uem_file_path = os.path.join(uem_dir, uem_filename)
            with open(uem_file_path, 'w') as f:
                # write the UEM line (session, channel, start_time, end_time)
                f.write(f'{session_name} 1 {uem_start_time} {uem_end_time}')
