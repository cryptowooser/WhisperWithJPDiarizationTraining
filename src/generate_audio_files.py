import os
import subprocess
from pathlib import Path
import shutil

def process_audio_file(input_file, output_dir):
    file_path = Path(input_file)
    file_name = file_path.stem
    file_extension = file_path.suffix.lower()

    # Extract audio if input is a video file
    if file_extension == '.avi':
        print(f"Extracting audio from video: {file_name}")
        audio_file = output_dir / f"{file_name}.mp3"
        subprocess.run(['ffmpeg', '-i', str(file_path), '-q:a', '0', str(audio_file)], check=True)
    else:
        audio_file = file_path

    # Run demucs for vocal extraction
    print(f"Running Demucs for vocal extraction: {file_name}")
    vocal_extracted_dir = output_dir / "vocal_extracted"
    subprocess.run(['demucs', '-n', 'htdemucs_ft', str(audio_file), '--two-stems', 'vocals', 
                    '-o', str(vocal_extracted_dir), '--filename', '{track}-{stem}.{ext}'], check=True)

    # Process the extracted vocals
    print(f"Processing extracted vocals: {file_name}")
    extracted_vocals = vocal_extracted_dir / "htdemucs_ft" / f"{file_name}-vocals.wav"
    enhanced_vocals = output_dir / f"{file_name}_vocals_16k_mono_enhanced.wav"
    subprocess.run(['ffmpeg', '-i', str(extracted_vocals), '-ar', '16000', '-ac', '1', '-acodec', 'pcm_s16le',
                    '-af', "aresample=resampler=soxr, lowpass=f=7500, acompressor=threshold=-12dB:ratio=2:attack=5:release=50, equalizer=f=1000:width_type=o:width=1:g=2, equalizer=f=3000:width_type=o:width=1:g=3",
                    '-b:a', '128k', str(enhanced_vocals)], check=True)

    # Rename the final output file
    final_output = output_dir / f"{file_name}.wav"
    os.rename(enhanced_vocals, final_output)

    # Cleanup
    print(f"Cleaning up temporary files: {file_name}")
    if file_extension == '.avi':
        os.remove(str(audio_file))
    
    # Remove vocal_extracted directory and its contents
    shutil.rmtree(str(vocal_extracted_dir), ignore_errors=True)

def generate_cleaned_audio_files(video_audio_files_location, processed_files_folder):
    output_dir = Path(processed_files_folder) / "prepped_audio"
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in Path(video_audio_files_location).glob('*'):
        if file.is_file():
            output_file = output_dir / f"{file.stem}.wav"
            if output_file.exists():
                print(f"Skipping file (already processed): {file.name}")
            else:
                print(f"Processing file: {file.name}")
                process_audio_file(file, output_dir)

    print("Processing complete!")
