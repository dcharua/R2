from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import portrait
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import StringIO
from num2words import num2words

#from tkinter import Tk, Menu, Canvas

        
def write_PDF(fecha, monto, beneficiario,concepto,notas,numero):     
    
    cv=canvas.Canvas("sample_PDF2")
    
    # Horizontal, Vertical
    #create a string
    cv.drawString(390, 770, fecha)
    
    # Fila 2
    cv.drawString(30, 710, beneficiario)
    cv.drawString(430, 710, str(monto))
    
    #Fila 3
    cv.drawString(30, 690, num2words(monto, lang='es').upper() + ' PESOS 00/100 M.N.')
    
    #Fila 3
    cv.drawString(160, 500, 'Concepto: ' + concepto + ' | Notas: ' + notas)
    cv.drawString(400, 500, '$' + str(monto))

    #Fila 5
    cv.drawString(400, 200, str(monto))
 
    #Fila 6
    cv.drawString(360, 180, str(numero))
 
    
    cv.save()
    
    
fecha, monto, beneficiario,concepto,notas,numero = '29/01/2019',4950.00,'AL PORTADOR','Luz','T-6 Luz',27280

write_PDF(fecha, monto, beneficiario,concepto,notas,numero)