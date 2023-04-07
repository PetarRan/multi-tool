from flask import Flask, render_template, make_response, request, url_for
import os
import moviepy.editor
import tempfile
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import pdf2docx

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

@app.route('/pdf-passprotect')
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
    # Get uploaded file
    pdf_file = request.files['pdf_file']


    # Load PDF file from request and convert to Word
    pdf_bytes = pdf_file.read()
    docx_bytes = pdf2docx.parse(BytesIO(pdf_bytes))

    # Create response and set headers to force download
    response = make_response(docx_bytes.getvalue())
    response.headers.set('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response.headers.set('Content-Disposition', 'attachment', filename='converted_document.docx')

    return response

############ End of Convert PDF ################

########### Static route ###########
@app.route('/static/<path:path>')
def serve_static(path):
    return app.send_static_file(path)
########### //////////// ###########

if __name__ == '__main__':
    app.run(debug=True)
