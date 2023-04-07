from flask import Flask, render_template, make_response, request, jsonify, url_for
import os
import moviepy.editor
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import pdf2docx
import speech_recognition as sr
import tempfile

app = Flask(__name__)

########### Navigation ######################

@app.route('/')
def home():
    return render_template('/index.html', static_folder='static')

@app.route('/merge-pdfs')
def merge_pdf():
    return render_template('/pdfmerge.html', static_folder='static')

@app.route('/extract-mp3')
def extract_mp3():
    return render_template('/mp3extract.html', static_folder='static')

@app.route('/convert-image')
def convert_images():
    return render_template('/imagesconvert.html', static_folder='static')

@app.route('/convert-pdf')
def convert_pdf():
    return render_template('/pdfconvert.html', static_folder='static')

@app.route('/transcibe-audio')
def transcribe():
    return render_template('/audiotranscibe.html', static_folder='static')

@app.route('/pdf-pass')
def passprotect():
    return render_template('/passprotectpdf.html', static_folder='static')

########### End of Navigation routes ###########

######### Pdf Merger Route ###########
@app.route('/merge-pdf-upload', methods=['POST'])
def upload_merge():
    pdf_files = request.files.getlist('pdf_file')

    writer = PdfWriter()

    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        # Loop through each page in the PDF file and add it to the writer object
        for i in range(len(reader.pages)):
            writer.add_page(reader.pages[i])

        # Save the merged PDF file to a byte stream
    output_stream = BytesIO()
    writer.write(output_stream)

    # Return the merged PDF file as a downloadable attachment
    response = make_response(output_stream.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=merged.pdf'
    response.headers['Content-Type'] = 'application/pdf'
    return response
######## END OF PDF MERGER ##########

########### Extract Mp3 Route ###########
@app.route('/extract-mp3-from-video', methods=['POST'])
def upload_for_extract():
    file = request.files.get('video_file')
    if not file:
        return "No file uploaded", 400
    filename, ext = os.path.splitext(file.filename)
    if ext not in ('.mp4', '.mov', '.wmv'):
        return "Invalid file type. Please upload a .mp4, .mov, or .wmv file.", 400

    filename = filename.replace(' ', '_')
    if not os.path.exists('temp'):
        os.makedirs('temp')
    file_path = os.path.join('temp', filename)
    file.save(file_path)

    video = moviepy.editor.VideoFileClip(file_path)
    audio = video.audio
    tmp_file_path = os.path.join('temp', 'exported.mp3')
    audio.write_audiofile(tmp_file_path)
    with open(tmp_file_path, 'rb') as f:
        mp3_data = BytesIO(f.read())

    os.remove(tmp_file_path)

    response = make_response(mp3_data.getvalue())
    response.headers.set('Content-Type', 'audio/mpeg')
    response.headers.set('Content-Disposition', 'attachment', filename='exported.mp3')
    return response

########### End of Mp3 Extract ###########

########### Convert Image route ##############

@app.route('/convert-image-action', methods=['POST'])
def convert_image():
    # Get uploaded file and output format from form
    image_file = request.files['image_file']
    output_format = request.form['output_format']

    # Load image from file
    image = Image.open(image_file)

    # Convert image to bytes and write to BytesIO buffer
    output_buffer = BytesIO()

    if output_format.upper() in {'JPEG', 'JPG'} and image.mode == 'RGBA':
        image = image.convert('RGB')
    

    image.save(output_buffer, format=output_format)
    output_buffer.seek(0)

    # Create response and set headers to force download
    response = make_response(output_buffer.read())
    response.headers.set('Content-Type', 'image/' + output_format)
    response.headers.set('Content-Disposition', 'attachment', filename='converted_image.' + output_format)

    return response

############ End of Convert Image ############

############# Convert PDF to Word #################

@app.route('/convert-pdf-to-docx', methods=['POST'])
def convert_pdf_to_docx():
    print("Something Else needs to be here!")
    
############ End of Convert PDF ################

############ Pass Protect PDF ################

@app.route('/protect-pdf', methods=['POST'])
def protect_pdf():
    # Get uploaded file and password
    pdf_file = request.files['file']
    password = request.form['password']

    # Load PDF file from request and create a PDF writer
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    # Add pages from the original PDF to the writer
    for i in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[i])

    # Encrypt the PDF with the password
    pdf_writer.encrypt(password)

    # Write the encrypted PDF to a memory buffer
    output_buffer = BytesIO()
    pdf_writer.write(output_buffer)
    output_buffer.seek(0)

    # Create a Flask response with the encrypted PDF as a downloadable file
    response = make_response(output_buffer.getvalue())
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename='protected.pdf')

    return response

############ End of Pass Protect PDF ################

############ Transcribe Audio #######################

@app.route('/transcribe', methods=['POST'])
def transcribe_action():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    # Check if file is uploaded
    if file.filename == '':
        return 'No file selected'

    # Check if file is mp3
    if file and file.filename.split('.')[-1].lower() == 'mp3':
        recognizer = sr.Recognizer()

        # Load audio file into memory
        audio_file = sr.AudioFile(file)
        with audio_file as source:
            audio = recognizer.record(source, duration=300)  # Limit duration to 5 minutes

        # Perform transcription
        try:
            text = recognizer.recognize_google(audio)
            return jsonify({'transcription': text})
        except sr.UnknownValueError:
            return 'Could not transcribe audio'
    else:
        return 'File type not supported'

############ End of Transcribe Audio ################

########### Static route ###########
@app.route('/static/<path:path>')
def serve_static(path):
    return app.send_static_file(path)
########### //////////// ###########

if __name__ == '__main__':
    app.run(debug=True)
