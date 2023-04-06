from pyPDF2 import PdfFileMerger
import os

merger = PdfFileMerger()
for items in os.listdir():
    if items.endswith('.pdf'):
        merger.append(items)

merger = write('merged.pdf')
merger = PdfFileMerger()
with open(originalFile, 'rb') as fin:
    merger.append(PdfFileMerger(fin))

os.remove(originalFile)
merger.close()