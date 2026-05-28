from flask import Flask, request, jsonify, send_file
from rembg import remove
from PIL import Image
import io
import base64

app = Flask(__name__)

@app.route('/api/remove-bg-base64', methods=['POST'])
def remove_background_base64():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'code': 400, 'message': '缺少图片数据'}), 400
        
        image_data = data['image']
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        img_bytes = base64.b64decode(image_data)
        input_image = Image.open(io.BytesIO(img_bytes)).convert('RGBA')
        output_image = remove(input_image)
        
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        result_base64 = base64.b64encode(img_io.read()).decode('utf-8')
        
        return jsonify({
            'code': 200,
            'message': '处理成功',
            'data': f'data:image/png;base64,{result_base64}'
        })
    
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@app.route('/api/remove-bg', methods=['POST'])
def remove_background():
    try:
        if 'file' not in request.files:
            return jsonify({'code': 400, 'message': '请上传图片'}), 400
        
        file = request.files['file']
        input_image = Image.open(file.stream).convert('RGBA')
        output_image = remove(input_image)
        
        img_io = io.BytesIO()
        output_image.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@app.route('/')
def index():
    return '<h1>Rembg API Service</h1><p>使用 POST /api/remove-bg-base64 或 /api/remove-bg</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
