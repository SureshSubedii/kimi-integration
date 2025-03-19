from flask import Flask, request, jsonify,session
from openai import OpenAI
import base64
import os
from flask_cors import CORS
import json


app = Flask(__name__)
CORS(app) 
# app.secret_key = os.urandom(24)  


UPLOAD_FOLDER = 'uploads/'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = OpenAI(
    api_key=os.environ.get("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
)



system_messages = [
    {"role": "system", "content": ''' You are a Dermatologist Expert. Bold the words important words and then suggest three questions to ask for remedies. The user will choose one of this question and then you will respond accordingly. You provide safe, helpful, and accurate responses to users.
    Please output your response in the following JSON format:
  {
    "message": "Result of analysis of the issue in a simple way for normal people",
    "q1": "First question ",
    "q2": "Second Question",
    "q3": "Third Question",

   }
   note: These are suggestion questions that the user might want to ask to you and not the questions that you ask to them.
   if the image is present add the following array key to the previous json format: {
    issues:[{
            "label": "name of the issue like acne, wrinkles, blackheads etc ",
            "x": "x coordinate of the isssue in the image in pixel",
            "y": "y coordinate  of the isssue in the image in pixel",
            "width": "width of the issue in the image",
            "height": "height of the issue"
        },]

        note there could be multiple issues in same image so you need to show them all in this issues json array.
        if the image is present and  the image is not clear or  the skin issue is difficult to identify due to this, ask the user to upload clear image and make sure you are absolutely correct and clear about your findings. 
    '''},

]

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    global system_messages
    messages = []

    if 'image' in request.files:
        file = request.files['image']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        with open(file_path, "rb") as f:
            image_data = f.read()    
        
        os.remove(file_path)  

        image_url = f"data:image/{os.path.splitext(file_path)[1]};base64,{base64.b64encode(image_data).decode('utf-8')}"

        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": request.form.get("query") or " Identiy the issue in the skin from the image"},
            ]
        }]
    else:
         messages.append({
        "role": "user",
        "content": request.form.get("query")    
    }) 


    messages.extend(system_messages)
    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k-vision-preview",
            messages= messages,
            temperature=0.3,
            response_format={"type": "json_object"}, 

        )
        assistant_message = completion.choices[0].message
        content = json.loads(assistant_message.content)
        print(content)
        return jsonify({"messages": content })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
