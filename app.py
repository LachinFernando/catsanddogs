
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
    labels.sort()

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

    #please add more features to here
    ################################
    ################################
st.write("continue up the app constructions")
#this magic command (%%writefile app.py) needs to be there to write the code into the app.py(Note: You can name the .py in any name)
#it is must to have the every code in the same code cell
import streamlit as st

st.title ("My first Web App")
st.header ("AIClub")
st.subheader("Navigator")
st.write("I love AIClub")
st.markdown("AI Club **Navigator** is really cool")

#!streamlit run app.py - This works locally. Since this is run on google cloud, we have to create a local port through a local tunnel
#for that we can use this
#!streamlit run app.py & npx localtunnel --port 8501

import streamlit as st
import requests
import json
from PIL import Image

#styleing
css_style = """
<style>
    .about {
        text-align: justfiy;
        border: 2px solid black;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: justify;
    }

    .about:hover {
        box-shadow: 0px 2px 1px grey;
    }

    .grid-container {
        display: grid;
        grid-template-columns: auto auto auto;
        padding: 15px;
        column-gap: 10px;
        row-gap: 10px;
        border: 2px solid black;
        border-radius: 10px;
    }

    .img {
        width: 200px;
        height: 200px;
        margin-left: 10px;
        transition: transform 2s;
    }

    .label {
        text-align: center;
        font-weight: bold;
        margin: 0px;
    }

    .img:hover {
        transform: scale(1.1);
        
    }

    .img:hover + p {
        margin-top: 10px;
    }

</style>
"""
#set css styles
st.markdown(css_style, unsafe_allow_html=True)

#####subscription key
subscription_key = '712fb8ca42394295b148d5d78769a25e'#prediction key

################################Needful Functions###################################
def get_prediction(image_data, header_data):
  #copy the URL
  url = 'https://yamunainstance1-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/a4ea8971-bfaf-48cf-8754-9bbf05343d2a/classify/iterations/Iteration1/image'
  r = requests.post(url,headers = header_data, data = image_data)
  response = json.loads(r.content)
  print(response)
  return response


#title of the web app
st.title("E Waste Classification")

