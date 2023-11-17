import requests
from flask import Flask, jsonify, render_template, request
import subprocess
import os
import time
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

    uploaded_data, upload_speed = save_files_locally(file_paths)

    return jsonify({
        'ping_result': ping_result,
        'download_speed': download_speed,
        'downloaded_data': downloaded_data,
        'uploaded_data': uploaded_data,
        'upload_speed': upload_speed
    })

def measure_ping():
    try:
        url = "https://www.google.com"
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        latency = end_time - start_time
        return f"Ping to {url}: {latency:.2f} seconds"
    except requests.RequestException as e:
        return f'Ping request failed: {e}'

def measure_download_speed(urls):
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
    avg_download_speed = sum(download_speeds) / len(download_speeds)
    return avg_download_speed, file_paths

def save_files_locally(file_paths):
    uploaded_data = 0
    upload_speed = 0
    for file_path in file_paths:
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            start_time = time.time()
            destination_path = f'/local_storage/{file_name}'
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.copyfile(file_path, destination_path)
            end_time = time.time()
            uploaded_data += file_size / (1024 * 1024)  # Convert bytes to megabytes
            upload_time = end_time - start_time
            upload_speed += (file_size * 8) / (upload_time * 1024 * 1024)  # Calculate upload speed in Mbps
        else:
            print(f"File not found: {file_path}")
    return uploaded_data, upload_speed

if __name__ == '__main__':
    app.run(debug=True)
