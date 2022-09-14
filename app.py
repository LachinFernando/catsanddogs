
import streamlit as st
import numpy as np
from PIL import Image
from io import BytesIO
from copy import deepcopy
import base64
import tensorflow as tf
from keras.applications.resnet import preprocess_input

#prediction function
def prediction(modelname, sample_image, IMG_SIZE = (224,224)):

    #labels
    labels = ["Cat","Dog"]

    try:
        #loading the .h5 model
        load_model = tf.keras.models.load_model(modelname)

        sample_image = base64.b64decode(sample_image)
        payload = bytearray(sample_image)
        stream = BytesIO(payload)
        img_array = Image.open(stream).convert("RGB")
        img_array = img_array.resize(IMG_SIZE)
        img_batch = np.expand_dims(img_array, axis = 0)
        img_batch = deepcopy(img_batch)
        image_batch = img_batch.astype(np.float32)
        image_batch = preprocess_input(image_batch)
        st.image(img_batch)
        prediction = load_model.predict(img_batch)
        return labels[int(np.argmax(prediction, axis = 1))]


    except Exception as e:
        st.write("ERROR: {}".format(str(e)))


#set the title according to your web app
st.title("Cats and Dogs Classifier")

#setting a sidebar
#you can chnage the desggn as your preference
with st.sidebar:

    #setting a subheader
    st.header("Sample Images")

    #setting subheader cats
    st.subheader("Cats")

    #setting pictures of cats
    st.image('cat1.jpg', caption = "A Cat")
    st.image("cat2.jpg", caption = "A Cat")

    #setting pictures of dogs
    st.subheader("Dogs")

    st.image('dog1.jpg', caption = "A Dog")
    st.image("dog2.jpg", caption = "A Dog")

#setting file uploader
#you can change the label name as your preference
image1 = st.file_uploader(label="Upload an image",accept_multiple_files=False, help="Upload an image to classify them")

if image1:

    #showing the image
    st.image(image1, "Image to be predicted")

    #file details
    #to get the file information
    file_details = {
      "file name": image1.name,
      "file type": image1.type,
      "file size": image1.size
    }

    #write file details
    st.write(file_details)

    #converting the image to bytes
    img = Image.open(image1)
    buf = BytesIO()
    img.save(buf,format = 'JPEG')
    byte_im = buf.getvalue()

    #converting bytes to b64encoding
    payload = base64.b64encode(byte_im)

    #image predicting
    label = prediction("best_model.h5",payload)
    st.subheader("This is a **{}**".format(label))

