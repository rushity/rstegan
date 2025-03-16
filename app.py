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

    # ✅ Step 4: Resize large images to max 1000px (to prevent mobile issues)
    if max(img.size) > 1000:  
        img.thumbnail((1000, 1000))

    encoded = img.copy()
    width, height = encoded.size
    pixels = encoded.load()

    message += '\0'  # Add null character to mark the end of the message

    index = 0
    for y in range(height):
        for x in range(width):
            if index < len(message):
                r, g, b = pixels[x, y][:3]  # Ignore alpha
                pixels[x, y] = (r, g, ord(message[index]))  # Store text in Blue channel
                index += 1

    # Save strictly as PNG to prevent compression
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

    # Convert any image format to RGB to avoid issues
    img = img.convert("RGB")

    pixels = img.load()
    width, height = img.size

    message = ""
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y][:3]  # Ignore alpha channel

            if b == 0:  # End of message
                break
            message += chr(b)

    message = message.rstrip('\0')  # Remove extra null characters

    return render_template('index.html', message=message)


@app.route('/')
def index():
    return render_template('index.html', message='')

if __name__ == '__main__':
    app.run(debug=True)
