# from numpy.core.fromnumeric import argmax
from flask import Flask
from pyngrok import ngrok
from flask import Flask,request, render_template, Response
import cv2
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import datetime
import os
port_no = 4500
global capture,frame

ngrok.set_auth_token("2FQazJeCRWqhvvfFTHH5aTp0tqP_7PyrETeEND3JBiJrZoNUY")
public_url = ngrok.connect(port_no).public_url

app = Flask(__name__)
# run_with_ngrok(app)

class_name = ['Pepper__bell___Bacterial_spot',
              'Pepper__bell___healthy',
              'Potato___Early_blight',
              'Potato___Late_blight',
              'Potato___healthy',
              'Tomato_Bacterial_spot',
              'Tomato_Early_blight',
              'Tomato_Late_blight',
              'Tomato_Leaf_Mold',
              'Tomato_Septoria_leaf_spot',
              'Tomato_Spider_mites_Two_spotted_spider_mite',
              'Tomato__Target_Spot',
              'Tomato__Tomato_YellowLeaf__Curl_Virus',
              'Tomato__Tomato_mosaic_virus',
              'Tomato_healthy']

model = load_model('/content/drive/MyDrive/deployment_model/Server/plant_disease_model.h5')
 
model.make_predict_function()

try:
    os.mkdir('./shots')
except OSError as error:
    pass

try:
    os.mkdir('./upload')
except OSError as error:
    pass


camera = cv2.VideoCapture(0)


def generate_frames():
    while True:

        # read the camera frame
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # global capture,frame
    # while True:
    #     success, frame = camera.read()
    #     if success:
    #         if(capture):
    #             capture=0
    #             now = datetime.datetime.now()
    #             p = os.path.sep.join(['shots', "shot_{}.png".format(str(now).replace(":",''))])
    #             cv2.imwrite(p, frame)

    #         try:
    #             ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
    #             frame = buffer.tobytes()
    #             yield (b'--frame\r\n'
    #                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    #         except Exception as e:
    #             pass
                
        # else:
        #     pass

    
    # ret,frame = cap.read() # return a single frame in variable `frame`

#     while(True):
#         ret,frame = cap.read()
#         cv2.imshow('img1',frame) #display the captured image
#         if cv2.waitKey(1) & 0xFF == ord('y'): #save on pressing 'y' 
#             cv2.imwrite('images/c1.jpg',frame)
#             cv2.destroyAllWindows()
#             break

# cap.release()


def predict_label(img_path):
    output = []
    i = image.load_img(img_path, target_size=(256, 256))
    i = image.img_to_array(i)/255.0
    i = i.reshape(1, 256, 256, 3)
    p = model.predict(i)
    output.append(class_name[np.argmax(p[0])])
    output.append(max(p[0]))
    return output
    


# routes
@app.route("/")
def main():
    return render_template("index.html")


@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=['POST','GET'])
def tasks():

    global frame,camera
    if request.method == 'POST':
        if request.form.get('click') == '1':
            global capture
            capture=1
            ret,frame = camera.read()
            now = datetime.datetime.now()
            # file_path = os.path.sep.join(['shots', "shot_{}.png".format(str(now).replace(":",''))])
            file_path = "/content/" + 'shots/' + "shot_{}.jpg".format(str(now).replace(":",''))
            cv2.imwrite(file_path, frame)
        else :
            capture = 0

          
        p2 = predict_label(file_path)
        
 
    return render_template("output.html", prediction=p2[0],confidence = (p2[1]*100),img_path = img_path)




@app.route("/submit", methods=['GET', 'POST'])
def get_output():
	if request.method == 'POST':
		img = request.files['my_image']

		img_path = "static/" + img.filename	
		img.save(img_path)

		p = predict_label(img_path)

	return render_template("output.html", prediction = p[0],confidence =(p(1)*100),img_path = img_path)


print(f"click here for website by globle link  {public_url}")
app.run(port=port_no)

# if __name__ =='__main__':
# 	# app.debug = True
# 	app.run(debug = True)
