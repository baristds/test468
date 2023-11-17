from flask import Flask, request, send_file
import os
import subprocess
import time

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Network Speed Test</h1>
    <p><a href="/ping">Test Ping</a></p>
    <p><a href="/download">Test Download Speed</a></p>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Test Upload Speed">
    </form>
    '''

@app.route('/ping')
def ping():
    # Replace 'google.com' with the target you want to ping
    response = subprocess.run(["ping", "-c 4", "google.com"], stdout=subprocess.PIPE)
    return '<pre>' + response.stdout.decode('utf-8') + '</pre>'

@app.route('/upload', methods=['POST'])
def upload():
    start_time = time.time()
    file = request.files['file']
    # Save the file temporarily
    file.save("temp_file")
    elapsed_time = time.time() - start_time
    os.remove("temp_file") # Clean up
    return f'Upload Time: {elapsed_time:.2f} seconds'

@app.route('/download')
def download():
    # Provide a large file to download
    return send_file('path_to_large_file', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
