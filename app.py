from flask import Flask, render_template, request, send_file
from PIL import Image
import io

import os
from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.route('/encode', methods=['POST'])
def encode():
    image = request.files['image']
    message = request.form['message']

    if not image or not message:
        return "Missing image or message", 400

    img = Image.open(image)

    # Convert JPG or other formats to PNG
    img = img.convert("RGB")

    # Resize large images (max 1000px) to avoid mobile issues
    if max(img.size) > 1000:  
        img.thumbnail((1000, 1000))

    encoded = img.copy()
    width, height = encoded.size
    pixels = encoded.load()

    message_length = len(message)
    message_bytes = [ord(char) for char in message]

    # Store message length in the first pixel
    r, g, b = pixels[0, 0][:3]
    pixels[0, 0] = (message_length // 256, message_length % 256, b)  # Store length in first pixel

    index = 0
    for y in range(height):
        for x in range(width):
            if x == 0 and y == 0:  # Skip the first pixel (used for length)
                continue

            if index < message_length:
                r, g, b = pixels[x, y][:3]
                pixels[x, y] = (r, g, message_bytes[index])  # Store message in Blue channel
                index += 1

    # Save as PNG
    output_path = "/tmp/stego.png"
    encoded.save(output_path, format="PNG")

    return send_file(output_path, mimetype='image/png', as_attachment=True, download_name='stego.png')





# Decode Text from Image
# Decode Text from Image
@app.route('/decode', methods=['POST'])
def decode():
    image = request.files['image']
    if not image:
        return "No image provided", 400

    img = Image.open(image)
    img = img.convert("RGB")

    pixels = img.load()
    width, height = img.size

    # Read message length from the first pixel
    message_length = (pixels[0, 0][0] * 256) + pixels[0, 0][1]

    message = ""
    index = 0
    for y in range(height):
        for x in range(width):
            if x == 0 and y == 0:  # Skip the first pixel (contains length)
                continue

            if index < message_length:
                r, g, b = pixels[x, y][:3]
                message += chr(b)
                index += 1
            else:
                break

    return render_template('index.html', message=message)



@app.route('/')
def index():
    return render_template('index.html', message='')

if __name__ == '__main__':
    app.run(debug=True)
