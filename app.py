from flask import Flask, render_template, request, send_file, jsonify
import tempfile
import shutil
import os
from transcribe_translate_tts import process_video  # assuming this handles the video

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400

    video_file = request.files['video']

    # Create a temporary working directory
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, 'input.mp4')
        video_file.save(input_path)
        print(f"✅ Video saved: {input_path}")

        # Process the video (transcribe, translate, dub)
        output_path = process_video(input_path, tmpdir)

        if not os.path.exists(output_path):
            return jsonify({'error': 'Output video not generated'}), 500

        # Move final output to a permanent safe location before cleanup
        final_output = os.path.join(os.getcwd(), "final_output.mp4")
        try:
            shutil.copy2(output_path, final_output)
            print(f"✅ Final video created and moved to: {final_output}")
        except Exception as e:
            print(f"❌ ERROR moving output file: {e}")
            return jsonify({'error': str(e)}), 500

    # Serve the copied file safely (outside the deleted tempdir)
    return send_file(final_output, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
