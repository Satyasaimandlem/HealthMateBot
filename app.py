from flask import Flask, redirect, render_template, request, url_for
import joblib
import tensorflow as tf
from PIL import Image
#from keras.preprocessing.image import img_to_array
from numpy import asarray
import numpy as np


app = Flask(__name__)


# Save the model
saved_model_path = r'C:\Users\nikhi\OneDrive\Documentos\Data606\model\kaggle_model\model.h5'

#Loading model
model = tf.keras.models.load_model(saved_model_path)
print(model.summary())


# Preparing and pre-processing the image
# Modify the preprocess_img function to resize the image to the correct size
def preprocess_img(img_path):
    op_img = Image.open(img_path)
    if op_img is None:
        print(f"Failed to load image: {img_path}")
        return
    op_img = op_img.convert('RGB')    # Convert image to RGB
    img_resize = op_img.resize((224,224))    # Resize original image
    img2arr = asarray(img_resize) / 255.0    # Normalize image
    img_reshape = img2arr.reshape(-1, 224, 224, 3)    # Resise image for model input
    print("Procressing ended")
    return img_reshape


# Predicting function
def predict_result(predict):
    print(predict)
    pred = model.predict(predict)
    print("Prediction", pred)
    return np.argmax(pred[0], axis=-1)

app = Flask(__name__, template_folder= r'C:\Users\nikhi\OneDrive\Documentos\Data606\templates',
             static_folder= r'C:\Users\nikhi\OneDrive\Documentos\Data606\static', static_url_path='/static')
UPLOAD_FOLDER = r'C:\Users\nikhi\OneDrive\Documentos\Data606\templates'


app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Home route
@app.route("/")
def main():
    return render_template("index.html")


# Prediction route
@app.route('/prediction', methods=['POST'])
def predict_image_file():
    try:
        # your prediction
        if request.method == 'POST': 
            filename = request.files['file'].filename 
            print("Allowed File", allowed_file(filename))          
            # Check if the file extension is allowed
                
            img = preprocess_img(request.files['file'].stream)
            pred = predict_result(img)
            return render_template("result.html", predictions=str(pred))

    except:
        error = "File cannot be processed, Sorry Try again."
        return render_template("result.html", err=error)


# Driver code
if __name__ == "__main__":
    app.run()
