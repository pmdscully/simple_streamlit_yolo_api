from flask import Flask, request
import time, os, shutil

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    timestamp = int(time.time())
    filepath = f'./tmp/image_{timestamp}.jpg'
    file.save(filepath)
    shutil.copy(filepath, './tmp/current_image.jpg')
    return 'File uploaded', 200

if __name__ == '__main__':
    os.makedirs('./tmp', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)