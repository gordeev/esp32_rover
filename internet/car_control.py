from flask import Flask, render_template, request, Response, redirect
import requests

app = Flask(__name__)

#python ./car_control.py    
#ngrok http 5001

ESP32_IP = "192.168.1.108"
ESP32_STREAM_PORT = "8081"
ESP32_CONTROL_PORT = "80"

@app.route('/')
def index():
    video_stream_url = '/video_stream'
    return render_template('index.html', video_stream_url=video_stream_url)

@app.route('/video_stream')
def video_stream():
    # Stream the video from the ESP32 camera
    stream_url = f'http://{ESP32_IP}:{ESP32_STREAM_PORT}/stream'
    try:
        response = requests.get(stream_url, stream=True)
        return Response(response.iter_content(chunk_size=1024),
                        content_type=response.headers['Content-Type'])
    except requests.exceptions.RequestException as e:
        print(f'Error fetching video stream: {e}')
        return "Video stream not available", 503

@app.route('/control', methods=['POST'])
def control():
    action = request.form.get('action')
    if action:
        try:
            # Map actions to the ESP32 endpoints.
            if action in ['go', 'back', 'left', 'right']:
                url = f'http://{ESP32_IP}:{ESP32_CONTROL_PORT}/{action}'
            elif action == 'stop':
                url = f'http://{ESP32_IP}:{ESP32_CONTROL_PORT}/stop'
            else:
                print(f'Unknown action: {action}')
                return '', 400

            response = requests.get(url)
            if response.status_code == 200:
                print(f'Successfully sent action: {action} to ESP32')
            else:
                print(f'Failed to send action: {action}. Status code: {response.status_code}')
        except requests.exceptions.RequestException as e:
            print(f'Error sending action: {action} - {e}')
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
