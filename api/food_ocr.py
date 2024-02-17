from flask_restful import Resource
from flask import request,make_response
import base64
from PIL import Image
import json
import io
import os
from ultralytics import YOLO

class foodOcr(Resource):
    def __init__(self):
        self.model = YOLO('best.pt')
    def post(self):
        base64Encoded = request.form['base64Encoded']
        image_b64 = base64.b64decode(base64Encoded)
        image_memory = Image.open(io.BytesIO(image_b64))
        image_memory.save('./static/images_foodOcr/new.jpg')
        results = self.model.predict(['./static/images_foodOcr/new.jpg'],save=True)
        print('results\n',results)
        print('results[0].save_dir\n', results[0].save_dir)
        with open(os.path.join(results[0].save_dir, 'new.jpg'),'rb') as f:
            base64Predicted= base64.b64encode(f.read()).decode('utf-8')
        print('base64Predicted\n',base64Predicted)
        return make_response(json.dumps({'base64': base64Predicted}, ensure_ascii=False))