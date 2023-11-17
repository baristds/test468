import requests
from flask import Flask, jsonify, render_template, request
import subprocess
import os
import time
import boto3

app = Flask(__name__)


# Route to serve HTML page
@app.route('/')
def index():
    return render_template('index.html')


# Route to perform speed test
@app.route('/speed-test', methods=['POST'])
def speed_test():
    urls_to_download = [
        'https://link.testfile.org/70MB',
        'https://link.testfile.org/15MB',
        'https://link.testfile.org/30MB',
        'https://link.testfile.org/60MB',
        'http://link.testfile.org/150MB'
    ]
    ping_result = measure_ping()
    download_speed, file_paths = measure_download_speed(urls_to_download)
    downloaded_data = sum(os.path.getsize(file_path) for file_path in file_paths) / (1024 * 1024)

    uploaded_data, upload_speed = upload_to_s3(file_paths, 'cs468')

    return jsonify({
        'ping_result': ping_result,
        'download_speed': download_speed,
        'downloaded_data': downloaded_data,
        'uploaded_data': uploaded_data,
        'upload_speed': upload_speed
    })


# Function to measure ping time
def measure_ping():
    try:
        output = subprocess.run(["ping", "-c", "4", "http://127.0.0.1:5000/"], capture_output=True, text=True, timeout=10)
        ping_data = output.stdout
        return ping_data
    except subprocess.TimeoutExpired:
        return 'Ping request timed out.'


def measure_download_speed(urls):
    try:
        download_speeds = []
        file_paths = []
        for url in urls:
            file = requests.get(url, stream=True)
            file.raise_for_status()
            start_time = time.time()
            file_path = f'./downloaded_file_{time.time()}'  # Unique file path
            with open(file_path, 'wb') as f:
                for chunk in file.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            file_paths.append(file_path)
            download_time = time.time() - start_time
            file_size = int(file.headers.get("content-length", 0))
            file_size_megabits = file_size * 8 / 1000000
            download_speed = file_size_megabits / download_time  # in Mbps
            download_speeds.append(download_speed)
        # Calculate average download speed
        avg_download_speed = sum(download_speeds) / len(download_speeds)
        return avg_download_speed, file_paths  # Returning both average speed and list of file paths

    except requests.RequestException as e:
        print(f"Error: {e}")
        return None, []

# Function to upload the file to AWS S3
def upload_to_s3(file_paths, bucket_name):
    # Specify AWS credentials explicitly
    s3 = boto3.client('s3', aws_access_key_id='AKIAYO5CC7I4Y3N7IVOE ', aws_secret_access_key='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')

    uploaded_data = 0
    upload_speed = 0

    for file_path in file_paths:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)  # Size of the file in bytes
            start_time = time.time()
            s3.upload_file(file_path, bucket_name, file_name)
            end_time = time.time()

            uploaded_data += file_size / (1024 * 1024)  # Convert bytes to megabytes
            upload_time = end_time - start_time
            upload_speed += (file_size * 8) / (upload_time * 1024 * 1024)  # Calculate upload speed in Mbps

        else:
            print(f"File not found: {file_path}")

    return uploaded_data, upload_speed

if __name__ == '__main__':
    app.run(debug=True)
