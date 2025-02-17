import textwrap, operator, base64, json, datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# from pyreportjasper import PyReportJasper
from django.core import serializers
from fpdf import FPDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from ..models import Prestamos, DetallePrestamos, MaestroCintas, DetalleProgramas, Videos
from django.http.response import HttpResponse, JsonResponse
import os
import io
from pathlib import Path
from django.db.models import Q
from PyPDF2 import PdfWriter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter, landscape
from django.db import connections
import json
from django.http import JsonResponse
from datetime import datetime
from django.db import connections

class PDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        BASE_DIR = Path(__file__).resolve().parent.parent
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media')    

        self.add_font('Montserrat', '',  os.path.join(MEDIA_ROOT, 'Montserrat-Regular.ttf'), uni=True)
        self.add_font('Montserrat', 'B', os.path.join(MEDIA_ROOT, 'Montserrat-Bold.ttf'), uni=True)
        self.q = q
        
    def header(self):
    
        self.image('media/images/EducaciónAprende.jpeg', x=10, y=8, w=50)
        self.image('media/images/logo-aprendemx.png', x=65, y=5, w=50)
        self.ln()

        self.set_font('Montserrat', 'B', 8)
        self.cell(485,1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(440,1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(525,1, 'Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(458,1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(80)

        if userDevuelve:
        
            email_institucional  = userDevuelve['Email']
            extension_telefonica = userDevuelve['Extension']
            nombre_completo      = userDevuelve['Devuelve']
            puesto               = userDevuelve['Puesto']
           
            self.set_xy(10.0, 33.0)
            self.cell(84, 10, 'Nombre:', 0, 0, 'L')
            self.set_xy(27.0, 35.0)
            self.cell(30.0, 6.0, nombre_completo, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Correo:', 0, 0, 'L')
            self.set_xy(27.0, 41.0)
            self.cell(30.0, 6.0, email_institucional, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Puesto:', 0, 0, 'L')
            self.set_xy(27.0, 47.0)
            self.cell(30.0, 6.0, puesto, 0, 0, 'L')
            self.ln(3.5)
            self.cell(86, 10, 'Extensión:', 0, 0, 'L')
            self.set_xy(27.0, 47.0)
            self.cell(30.0, 6.0, extension_telefonica, 0, 0, 'L')
            self.ln(15)         
            self.set_font('Montserrat', 'B', 8)
            self.cell(280, 10, f'Prestamos de la cinta ({self.q})', 0, 0, 'C')
            self.ln(15)

            self.set_fill_color(144, 12, 63)
            self.set_text_color(255, 255, 255) 
            self.cell(40, 10, 'Folio', 1, 0, '', True)
            self.cell(40, 10, 'Usuario', 1, 0, '', True)
            self.cell(80, 10, 'Fecha y Hora Prestamo', 1, 0, '', True)
            self.cell(80, 10, 'Fecha de devolución', 1, 0, '', True)
            self.cell(40, 10, 'Estatus', 1, 0, '', True)
            self.set_text_color(0, 0, 0)
            self.ln()
            
    def footer(self):
        self.set_font('Montserrat', 'B', 8)

        if userRecibe:
          
            name  = userRecibe['Recibe']        
            self.set_xy(90.0, 33.0)
            self.cell(180, 10, 'Recibe:', 0, 0, 'L')
            self.set_xy(108.0, 35.0)
            self.cell(30.0, 6.0, name, 0, 0, 'L')

        if userDevuelve:
           
            name  = userDevuelve['Devuelve']          
            self.set_xy(90.0, 39.0)
            self.cell(180, 10, 'Devuelve:', 0, 0, 'L')
            self.set_xy(108.0, 41.0)
            self.cell(30.0, 6.0, name, 0, 0, 'L')
            self.set_xy(90.5, 50.0)
            self.cell(180, 10, 'Firma:', 0, 0, 'L')
            x = self.get_x()
            y = self.get_y()
            self.line(x - 167, y + 6, x - 120, y + 6)
            self.set_y(-15)
            self.set_font('Montserrat', '', 8)
            self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')



    def generate_table(self, data):
       
        for row in data:
            self.cell(40, 10, str(row['pres_folio']), 1)
            self.cell(40, 10, str(row['usua_clave']), 1)
            self.cell(80, 10, str(row['pres_fechahora']), 1)
            self.cell(80, 10, str(row['pres_fecha_devolucion']), 1)
            self.cell(40, 10, str(row['pres_estatus']), 1)
            self.ln()

def generar_pdf(request):
    q = request.GET.get('q')
    detalle_prestamos = DetallePrestamos.objects.filter(Q(pres_folio=q) | Q(vide_codigo=q), usuario_devuelve__isnull=False, usuario_recibe__isnull=False)
    pres_folios = detalle_prestamos.values_list('pres_folio_id', flat=True)

    prestamos_data = []

    for pres_folio_id in pres_folios:
        prestamo = Prestamos.objects.filter(pres_folio=pres_folio_id).first()
        if prestamo:
            if detalle_prestamos.filter(pres_folio=pres_folio_id).exists():
                prestamo_data = {
                    "pres_folio":            prestamo.pres_folio,
                    "usua_clave":            prestamo.usua_clave,
                    "pres_fechahora":        prestamo.pres_fechahora,
                    "pres_fecha_devolucion": prestamo.pres_fecha_devolucion,
                    "pres_estatus":          prestamo.pres_estatus,
                    "usuario_devuelve":      detalle_prestamos.filter(pres_folio=pres_folio_id).last().usuario_devuelve,
                    "usuario_recibe":        detalle_prestamos.filter(pres_folio=pres_folio_id).last().usuario_recibe,
                }
                prestamos_data.append(prestamo_data)
    usuarioDevuelve = prestamos_data[-1]['usuario_devuelve'] if   prestamos_data else ''
    usuarioRecibe   = prestamos_data[-1]['usuario_recibe']   if   prestamos_data else ''

    detalle_matricula = DetallePrestamos.objects.filter(usuario_devuelve=usuarioDevuelve).first()
    muestraData = []

    if detalle_matricula is not None:
        matricula_data = {
            "UsuarioDevuelve": detalle_matricula.usuario_devuelve,
            "UsuarioRecibe"  : detalle_matricula.usuario_recibe
        }
        muestraData.append(matricula_data)
        if muestraData:
            usuario_devuelve = muestraData[0]["UsuarioDevuelve"]
            usuario_recibe   = muestraData[0]["UsuarioRecibe"]

    cursor = connections['users'].cursor()
    # cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [usuario_devuelve])
    cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [usuario_devuelve])

    row = cursor.fetchone()

    if row is not None:
        nombres                 = row[0]
        apellido1               = row[1]
        apellido2               = row[2]
        puesto                  = row[3]
        email_institucional     = row[4]
        extension_telefonica    = row[5]

        nombre_completo = f"{nombres} {apellido1} {apellido2}" if apellido2 else f"{nombres} {apellido1}"
        MatriculaDevuelve = {
            'Devuelve'          : nombre_completo,
            'Puesto'            : puesto,
            'Email'             : email_institucional,
            'Extension'         : extension_telefonica, 
            'Matricula'         : usuario_devuelve,
        }

    cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [usuario_recibe])
    row = cursor.fetchone()

    if row is not None:
        nombres                 = row[0]
        apellido1               = row[1]
        apellido2               = row[2]
        puesto                  = row[3]
        email_institucional     = row[4]
        extension_telefonica    = row[5]

        nombre_completo2 = f"{nombres} {apellido1} {apellido2}" if apellido2 is not None else f"{nombres} {apellido1}"
        MatriculaRecibe = {
            'Recibe'            : nombre_completo2,
            'Puesto'            : puesto,
            'Email'             : email_institucional,
            'Extension'         : extension_telefonica, 
            'Matricula'         : usuario_recibe,
        }   
    global userDevuelve, userRecibe
    # global 
    userDevuelve = MatriculaDevuelve
    userRecibe = MatriculaRecibe

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Videoteca_Código_{q}.pdf"'
    pdf = PDF('P', 'mm', (300, 350), q)
    pdf.add_page()
    # pdf.footer(userDevuelve=userDevuelve, userRecibe=userRecibe)


    pdf.generate_table(prestamos_data)
    response.write(pdf.output(dest='S').encode('latin1'))
    return response

# ---------------------------------PDF2-----------------------------------#
# @csrf_exempt    
class GENERATE(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        BASE_DIR = Path(__file__).resolve().parent.parent
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media')    
        # print(font_folder)

        self.add_font('Montserrat', '', os.path.join(MEDIA_ROOT, 'Montserrat-Regular.ttf'), uni=True)
        self.add_font('Montserrat', 'B', os.path.join(MEDIA_ROOT, 'Montserrat-Bold.ttf'), uni=True)
        self.q = q

    def header(self):
        
        self.image('media/images/EducaciónAprende.jpeg', x=10, y=8, w=50)
        self.image('media/images/logo-aprendemx.png', x=65, y=5, w=50)
        self.ln()

        self.set_font('Montserrat', 'B', 8)
        self.cell(485,1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(440,1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(525,1, 'Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(458,1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(80)

        if userDevuelve:
        
            email_institucional  = userDevuelve['Email']
            extension_telefonica = userDevuelve['Extension']
            nombre_completo      = userDevuelve['Devuelve']
            puesto               = userDevuelve['Puesto']
           
            self.set_xy(10.0, 33.0)
            self.cell(84, 10, 'Nombre:', 0, 0, 'L')
            self.set_xy(27.0, 35.0)
            self.cell(30.0, 6.0, nombre_completo, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Correo:', 0, 0, 'L')
            self.set_xy(27.0, 41.0)
            self.cell(30.0, 6.0, email_institucional, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Puesto:', 0, 0, 'L')
            self.set_xy(27.0, 47.0)
            self.cell(30.0, 6.0, puesto, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Extensión:', 0, 0, 'L')
            self.set_xy(27.0, 47.0)
            self.cell(30.0, 6.0, extension_telefonica, 0, 0, 'L')
            self.ln(15)         
            self.set_font('Montserrat', 'B', 8)
            self.cell(280, 10, f'Prestamos de la cinta ({self.q})', 0, 0, 'C')
            self.ln(15)

            self.set_fill_color(31, 237, 237)
            self.set_text_color(255, 255, 255) 
            self.cell(140, 10, 'Código de Barras', 1, 0, '', True)
            self.cell(140, 10, 'Fecha de Devolucón', 1, 0, '', True)
            self.set_text_color(0, 0, 0)
            self.ln(10)
    
    def footer(self):
        self.set_font('Montserrat', 'B', 8)

        if userRecibe:
          
            name  = userRecibe['Recibe']        
            self.set_xy(90.0, 33.0)
            self.cell(180, 10, 'Recibe:', 0, 0, 'L')
            self.set_xy(108.0, 35.0)
            self.cell(30.0, 6.0, name, 0, 0, 'L')

        if userDevuelve:
           
            name  = userDevuelve['Devuelve']          
            self.set_xy(90.0, 39.0)
            self.cell(180, 10, 'Devuelve:', 0, 0, 'L')
            self.set_xy(108.0, 41.0)
            self.cell(30.0, 6.0, name, 0, 0, 'L')
            self.set_xy(90.5, 50.0)
            self.cell(180, 10, 'Firma:', 0, 0, 'L')
            x = self.get_x()
            y = self.get_y()
            self.line(x - 167, y + 6, x - 120, y + 6)
            self.set_y(-15)
            self.set_font('Montserrat', '', 8)
            self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')

    def generate_Table(self, data):
       
        for row in data:
            self.cell(140, 10, str(row['vide_codigo']), 1)
            fecha_devolucion = row['pres_fecha_devolucion'].strftime('%d-%m-%Y')
            self.cell(140, 10, fecha_devolucion, 1)
            self.ln(10)
            
def generar_pdf_modal(request):

    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo', 'pres_fecha_devolucion', 'usuario_devuelve', 'usuario_recibe')
    detalle_prestamos = queryset.last() if queryset else None 
    # fecha = detalle_prestamos['pres_fecha_devolucion'].strftime('%d-%m-%Y')
    # print(fecha)
    
    if detalle_prestamos:
        usuario_devuelve = detalle_prestamos['usuario_devuelve']
        usuario_recibe = detalle_prestamos['usuario_recibe']
        # 
        detalle_matricula = DetallePrestamos.objects.filter(usuario_devuelve=usuario_devuelve).first()
        muestraData = []

        if detalle_matricula is not None:
            matricula_data = {
                "UsuarioDevuelve": detalle_matricula.usuario_devuelve,
                "UsuarioRecibe"  : detalle_matricula.usuario_recibe
            }
            muestraData.append(matricula_data)
            if muestraData:
                usuario_devuelve = muestraData[0]["UsuarioDevuelve"]
                usuario_recibe   = muestraData[0]["UsuarioRecibe"]

        cursor = connections['users'].cursor()
        cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [usuario_devuelve] )
        # cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica FROM people_person WHERE matricula = %s OR matricula = %s", [usuario_devuelve, usuario_recibe])

        row = cursor.fetchone()

        if row is not None:
            nombres                 = row[0]
            apellido1               = row[1]
            apellido2               = row[2]
            puesto                  = row[3]
            email_institucional     = row[4]
            extension_telefonica    = row[5]

        nombre_completo = f"{nombres} {apellido1} {apellido2}" if apellido2 else f"{nombres} {apellido1}"
        
        MatriculaDevuelve = {
            'Devuelve'              : nombre_completo,
            'Puesto'                : puesto,
            'Email'                 : email_institucional,
            'Extension'             : extension_telefonica, 
            'Matricula'             : usuario_devuelve,
        }

        cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [usuario_recibe])
        row = cursor.fetchone()

        if row is not None:
            nombres                 = row[0]
            apellido1               = row[1]
            apellido2               = row[2]
            puesto                  = row[3]
            email_institucional     = row[4]
            extension_telefonica    = row[5]
            
            nombre_completo2 = f"{nombres} {apellido1} {apellido2}" if apellido2 else f"{nombres} {apellido1}"
            MatriculaRecibe = {
                'Recibe'            : nombre_completo2,
                'Puesto'            : puesto,
                'Email'             : email_institucional,
                'Extension'         : extension_telefonica, 
                'Matricula'         : usuario_recibe,
            }

        global userDevuelve, userRecibe
        userDevuelve = MatriculaDevuelve
        userRecibe = MatriculaRecibe

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Videoteca_Código_{q}.pdf"'
    pdf = GENERATE('P', 'mm', (300, 350), q)
    pdf.add_page()
    pdf.generate_Table(queryset)
    response.write(pdf.output(dest='S').encode('latin1'))
    return response
# ---------------------------------------------------------------------------------------------------------------------------#

@csrf_exempt      
def json_to_pdf(request,fechaInicio,fechaFin,folio  ):
    dateInicio = datetime.datetime.strptime(fechaInicio, "%d-%m-%Y")
    dateFin = datetime.datetime.strptime(fechaFin, "%d-%m-%Y")
 
    
    input_file = settings.MEDIA_ROOT+ '/Formatos/Compensacion_v1.jrxml'
    CreateJson(dateInicio, dateFin, None, folio)
    output_file = settings.MEDIA_ROOT+ '/Formatos'
    
    json_query = 'contacts.person'

    
    #dictionary = {"contacts": {"person": [ {'Folio':34, 'RFC':61, 'Nombre':82, 'ClaveP':82, 'Categoria':82, 'Codigo':82, 'Compensacion':82, 'CostoHora':82, 'HorasXMes':82, 'Importe':82, 'Fecha':82, 'NoFolio':82}  ] } } 
    #jsonString = json.dumps(dictionary, indent=4)

    #print(jsonString)
    conn = {
      'driver': 'json',
      'data_file': settings.MEDIA_ROOT+ '/Formatos/data.json',
      'json_query': 'compensacion'
   }
    outputFile= settings.MEDIA_ROOT+ '/Formatos/ReporteCompensacion '+fechaInicio+' al '+fechaFin+'.pdf' 
    pyreportjasper = PyReportJasper()
    pyreportjasper.config(
      input_file,
      output_file=outputFile,
      output_formats=["pdf"],
      db_connection=conn
   )
    pyreportjasper.process_report()
    print('Result is the file below.')
   # output_file = output_file + '.pdf'
    if os.path.isfile(outputFile):
    #    print('Report generated successfully!')
        with open(outputFile, 'rb') as pdf:
            response = HttpResponse(pdf.read(),content_type='application/pdf')
            response['Content-Disposition'] = 'filename=ReporteCompensacion '+fechaInicio+' al '+fechaFin+'.pdf'
        return response


def CreateJsonInReport(row, codes, user):
    data = {}
    now = datetime.datetime.now()
    data['reporte']=[]
    data['header'].append({'Nombre': row[0][0] + ' '+ row[0][1]+ ' '+ row[0][2],
                'Direccion':  row[0][5],
                'Puesto':  row[0][6],
                'Extension': row[0][3],
                'Correo':   row[0][4] ,
                'Matricula':   row[0][7],
                'FechaDev': now,
                'Recibe': user,
                'Logo1': settings.MEDIA_ROOT+ '/Formatos/logo-sep.png', 
                'Logo2':  settings.MEDIA_ROOT+ '/Formatos/logo-aprendemx.png' })
                
    with open(settings.MEDIA_ROOT+ '/Formatos/dataHeader.json', 'w',  encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False) 
   
