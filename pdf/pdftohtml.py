# -*- coding: utf-8 -*-
__author__ = 'Memray'
import os;
sigir_path = 'H:\\acm_dl\\pdf\\ir\\'
pdftotext_path = 'H:\\Dropbox\\PhD@Pittsburgh\\3.LAB\\20150908_pdfextract\\PdfMagick_text\\poppler-0.36\\bin\\pdftotext.exe'
for filename in os.listdir(sigir_path):
    if not filename.lower().endswith('pdf'):
        continue
    cmd_str = pdftotext_path+' -bbox '+sigir_path+filename+" "+sigir_path+filename[0:-4]+'_pdftotext.html'
    # print filename+' : '+filename[0:-4]
    print cmd_str
    os.system(cmd_str)


