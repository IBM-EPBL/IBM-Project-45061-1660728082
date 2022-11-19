import numpy as np
import os
from flask import Flask, app,request,render_template,redirect,url_for,session
from tensorflow.keras import models
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.python.ops.gen_array_ops import concat
from tensorflow.keras.applications.inception_v3 import preprocess_input
import requests
import webbrowser

os.add_dll_directory

#creating the Cloudant Database 
from cloudant.client import Cloudant
client = Cloudant.iam("91c10fc0-d855-461f-b829-2400514b5ec8-bluemix","hBZgxthND7_FU-UQs9ddhKKJzzgKN3yyOhBKdtKfrE65",connect=True)
database = client.create_database("my_database")



#load model
model1 = load_model(r'C:/Users/Karthik P/Music/Final Deliverables/Model/body.h5')
model2 = load_model(r'C:/Users/Karthik P/Music/Final Deliverables/Model/level.h5')

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

#login page setting 

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/afterlogin',methods=['POST','GET'])
def afterlogin():
    user = request.form['_id']
    passw = request.form['psw']
    print(user,passw)

    query = {'_id':{'$eq':user}}

    docs = database.get_query_result(query)
    print(docs)
    print(len(docs.all()))

    if(len(docs.all())==0):
        return render_template('login.html',message='The username is not found')
    else:
        if((user==docs[0][0]['_id'] and passw==docs[0][0]['psw'])):
            return redirect(url_for('prediction'))
        else:
            return render_template("login.html",message="Invalid User Details")
    

#Register page setting 

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/afterreg',methods=['POST'])
def afterregister():
    x = [x for x in request.form.values()]
    print(x)
    data = {
        '_id':x[1],
        'name':x[0],
        'psw' : x[2]
    }
    print(data)

    query = {'_id':{'$eq' : data['_id']}}
    docs = database.get_query_result(query)

    if(len(docs.all())==0):
        url = database.create_document(data)
        return render_template('register.html', message="Registration is Successfully Completed")
    else:
        return render_template("register.html", message="You are already a member!")

#prediction

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

#logout page 

@app.route('/logout')
def logout():
    return render_template('logout.html')

#results 
from os.path import join, dirname, realpath

@app.route('/result', methods = ['GET', 'POST'])
def result():
   if request.method=="POST":
        f=request.files['file']
        basepath=os.path.dirname("__file__")
        filepath=os.path.join(basepath,'Static/Uploads', f.filename)
        f.save(filepath)
        img=image.load_img(filepath,target_size=(224, 224))   
        x=image.img_to_array(img)
        x=np.expand_dims(x,axis=0)
        img_data=preprocess_input(x)
        prediction1=np.argmax(model1.predict(img_data))
        prediction2=np.argmax(model2.predict(img_data))
        index1=['front','rear','side']
        index2=['minor','moderate','severe']
        result1=index1[prediction1]
        result2=index2[prediction2]
        print(result1)
        print(result2)
        if(result1=="front"and result2=="minor"):
            value="3000 - 5000 INR"
        elif(result1=="front"and result2=="moderate"):
            value="6000 - 8000 INR"
        elif(result1=="front"and result2=="severe"):
            value="9000 - 11000 INR"
        elif(result1=="rear"and result2=="minor"):
            value="4000 - 6000 INR"
        elif(result1=="rear"and result2=="moderate"):
            value="7000 - 9000 INR"
        elif(result1=="rear"and result2=="severe"):
            value="11000 - 13000 INR"
        elif(result1=="side"and result2=="minor"):
            value="6000 - 8000 INR"
        elif(result1=="side"and result2=="moderate"):
            value="9000 - 11000 INR"
        elif(result1=="side"and result2=="severe"):
            value="12000 - 15000 INR"
        else:
            value="16000 - 50000 INR"
        return render_template("result.html", prediction=value,ayya=result1,amma=result2)
    
if (__name__ == '__main__'):
    app.run(debug=True)