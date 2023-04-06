from flask import Flask, render_template, make_response, request, url_for
import os
import moviepy.editor
import tempfile
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

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
    return render_template('/extractmp3.html', static_folder='static')

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

########### Static route ###########
@app.route('/static/<path:path>')
def serve_static(path):
    return app.send_static_file(path)
########### //////////// ###########

if __name__ == '__main__':
    app.run(debug=True)
