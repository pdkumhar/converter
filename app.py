from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from moviepy import VideoFileClip
import logging
import subprocess

app = Flask(__name__)

# Set upload and converted folders
UPLOAD_FOLDER = 'static/uploads'
CONVERTED_FOLDER = 'static/converted'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# Set up logging to capture errors
logging.basicConfig(level=logging.DEBUG)

# Dynamically locate the FFMPEG binary relative to the project directory
FFMPEG_PATH = os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe')

# Validate the FFMPEG path
if not os.path.isfile(FFMPEG_PATH):
    logging.error(f"FFMPEG binary not found at: {FFMPEG_PATH}. Please ensure it exists.")
    raise FileNotFoundError(f"FFMPEG executable not found at {FFMPEG_PATH}")

# Set the environment variable for ffmpeg
os.environ['FFMPEG_BINARY'] = FFMPEG_PATH


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_page():
    """Render the upload page."""
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and conversion."""
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    format = request.form['format']  # Get the selected format
    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Convert video after upload
        input_path = filepath
        output_filename = f"{os.path.splitext(filename)[0]}.{format}"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)

        try:
            if format.lower() == 'wmv':
                # Use ffmpeg for WMV conversion
                ffmpeg_command = [
                    FFMPEG_PATH,  # Full path to ffmpeg executable
                    '-y',  # Overwrite output file without prompting
                    '-i', input_path,
                    '-c:v', 'wmv2',  # WMV video codec
                    '-c:a', 'wmav2',  # WMV audio codec
                    output_path
                ]
                subprocess.run(ffmpeg_command, check=True)
            else:
                # Use MoviePy for other formats
                clip = VideoFileClip(input_path)
                clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

            # Ensure the converted file exists
            if os.path.exists(output_path):
                return render_template('upload.html', download_filename=output_filename)
            else:
                return render_template('upload.html', message="Error in video conversion.")

        except Exception as e:
            return render_template('upload.html', message=f"Error during conversion: {str(e)}")


@app.route('/download/<filename>')
def download_video(filename):
    """Allow the user to download the converted video."""
    try:
        # Ensure the file exists before trying to send it
        return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error in file download: {e}")
        return "Error in downloading the video."


if __name__ == '__main__':
    app.run(debug=True)