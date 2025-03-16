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

    filename = secure_filename(image.filename)
    filepath = os.path.join("/tmp", filename)
    image.save(filepath)  # Save file temporarily

    img = Image.open(filepath)

    # Ensure image is in RGB mode
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    encoded = img.copy()
    width, height = encoded.size
    pixels = encoded.load()

    message += '\0'  # Add null character to mark the end of the message

    index = 0
    for y in range(height):
        for x in range(width):
            if index < len(message):
                pixel = pixels[x, y]

                if len(pixel) == 4:  # If the image has an alpha channel
                    r, g, b, a = pixel
                    pixels[x, y] = (r, g, ord(message[index]), a)  # Preserve alpha
                else:
                    r, g, b = pixel
                    pixels[x, y] = (r, g, ord(message[index]))

                index += 1

    output_path = os.path.join("/tmp", "stego.png")
    encoded.save(output_path, format="PNG")

    return send_file(output_path, mimetype='image/png', as_attachment=True, download_name='stego.png')



# Decode Text from Image
# Decode Text from Image
@app.route('/decode', methods=['POST'])
def decode():
    image = request.files['image']
    if not image:
        return "No image provided", 400

    filename = secure_filename(image.filename)
    filepath = os.path.join("/tmp", filename)
    image.save(filepath)  # Save file temporarily

    img = Image.open(filepath)

    # Ensure image is in RGB mode
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    pixels = img.load()
    width, height = img.size

    message = ""
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]

            if len(pixel) == 4:  # If the image has an alpha channel
                r, g, b, a = pixel
            else:
                r, g, b = pixel

            if b == 0:  # End of message
                break
            message += chr(b)

    message = message.rstrip('\0')  # Remove trailing null character

    return render_template('index.html', message=message)


@app.route('/')
def index():
    return render_template('index.html', message='')

if __name__ == '__main__':
    app.run(debug=True)
