from django.views.generic import ListView
from ..models import Prestamos, DetallePrestamos, MaestroCintas, DetalleProgramas, Videos
from ..forms import PrestamoInlineFormset
from django.shortcuts import render
from functools import reduce
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import textwrap, operator, base64, json, datetime
from django.template.loader import get_template
from django.db.models import Q
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.core import serializers
from fpdf import FPDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.shortcuts import get_object_or_404
import tempfile


    # ---------------------------
    # Prestamos
    # ---------------------------

@method_decorator(login_required, name='dispatch')
class PrestamosListView(ListView):
    def get(self, request):
        queryset = Prestamos.objects.filter(Q(pres_fecha_prestamo__year='2022')).order_by('-pres_fechahora')
        context = {
            'prestamos': queryset,
        }
        return render(request, 'prestamos/prestamos_list.html', context)
    

@csrf_exempt
def PrestamoDetalle(request):
    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo', 'pres_fecha_devolucion')
    context = { 'detalles': queryset }
    return render(request, 'prestamos/prestamos_detalle_list.html', context)

def Filtrar_prestamos(request):
    q = request.GET.get('q')

    # Obtener los pres_folio que coinciden con el vide_codigo
    pres_folios = DetallePrestamos.objects.filter(vide_codigo_id=q).values_list('pres_folio_id', flat=True)

    # Crear una lista para almacenar los datos de prestamos
    prestamos_data = []

    # Obtener los datos de Prestamos para cada pres_folio encontrado
    for pres_folio_id in pres_folios:
        prestamo = Prestamos.objects.filter(pres_folio=pres_folio_id).first()
        if prestamo:
            # Acceder a los datos de Prestamos
            prestamo_data = {
                "pres_folio": prestamo.pres_folio,
                "usua_clave": prestamo.usua_clave,
                "pres_fechahora": prestamo.pres_fechahora,  
                "pres_fecha_devolucion": prestamo.pres_fecha_devolucion,
                "pres_estatus": prestamo.pres_estatus
            }
            
            prestamos_data.append(prestamo_data)

    # Retornar los datos de prestamos en formato JSON
    return JsonResponse(prestamos_data, safe=False)


# class PDF(FPDF):
#     def generate_pdf(self, data):
#         # Convertir los datos JSON a una lista de Python
#         data = json.loads(data)
#         # Configurar la página y la fuente
#         self.add_page()
#         self.set_font('Arial','B',16)
#         # Agregar el título
#         self.cell(40, 10, 'PDF VIDEOTECA', 0 , 1)
#         # Agregar los datos
#         for row in data:
#             self.cell(40,10, str(row['pres_folio']), 1)
#             self.cell(40,10, str(row['usua_clave']), 1)
#             self.cell(40,10, str(row['pres_fechahora']), 1)
#             self.cell(40,10, str(row['pres_fecha_devolucion']), 1)
#             self.cell(40,10, str(row['pres_estatus']), 1)
#             self.ln()

# @csrf_exempt
# def generar_pdf(request):
#     # Obtener los datos de la solicitud AJAX
#     data = request.GET.getlist('data[]')
#     # Generar el PDF
#     pdf = PDF()
#     pdf.generate_pdf(data)
#     # Retornar el PDF como una respuesta HTTP
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
#     pdf_output = pdf.output(dest='S').encode('latin1')
#     response.write(pdf_output)
#     return response

# ---------------------------------------------------------------------------------------------------------------------------#

class PDF(FPDF):

    def header(self):
        # Configuración de la cabecera del PDF
        # self.image('https://framework-gb.cdn.gob.mx/landing/img/logoheader.svg', x=10, y=8, w=33)
        # self.image('C:\Users\MIJIMENEZ\Desktop\videoteca\images', 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        # self.cell(80)
        self.cell(30, 10, 'Videoteca', 1, 0, 'C')
        self.ln(10)

    def footer(self):
        # Configuración del pie de página del PDF
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')

    def generate_pdf(self, data):
        # Generación del contenido del PDF
        self.add_page()
        # self.set_size('A4', 'L') # or whatever page size and orientation you want
        self.set_font('Arial', 'B', 12)
        for row in data:
            # self.cell(40,10, str(row['pres_folio']), 1)
            # self.cell(40,10, str(row['usua_clave']), 1)
            # self.cell(40,10, str(row['pres_fechahora']), 1)
            # self.cell(40,10, str(row['pres_fecha_devolucion']), 1)
            # self.cell(40,10, str(row['pres_estatus']), 1)

            self.cell(40,10, str(row[0]), 1)  # Usar el índice 0 en lugar de 'Folio'
            self.cell(40,10, str(row[1]), 1)  # Usar el índice 1 en lugar de 'Usuario'
            self.cell(40,10, str(row[2]), 1)  # Usar el índice 2 en lugar de 'Fecha y Hora Prestamo'
            self.cell(40,10, str(row[3]), 1)  # Usar el índice 3 en lugar de 'Fecha de devolución'
            self.cell(40,10, str(row[4]), 1)  # Usar el índice 4 en lugar de 'Estatus'
            self.ln()

def generar_pdf(request):

    q = request.GET.get('q')
    # Obtener los pres_folios que coinciden con el vide_codigo
    detalle_prestamos = DetallePrestamos.objects.filter(vide_codigo=q)
    pres_folios = detalle_prestamos.values_list('pres_folio_id', flat=True)
    # Obtener los datos de prestamos para cada pres_folio encontrado
    prestamos_data = []
    for pres_folio_id in pres_folios:
        prestamo = Prestamos.objects.filter(pres_folio=pres_folio_id).first()
        if prestamo:
            # Acceder a los datos de prestamos
            prestamo_data = {
                "pres_folio": prestamo.pres_folio,
                "usua_clave": prestamo.usua_clave,
                "pres_fechahora": prestamo.pres_fechahora,
                "pres_fecha_devolucion": prestamo.pres_fecha_devolucion,
                "pres_estatus": prestamo.pres_estatus
            }
            prestamos_data.append(prestamo_data)

            

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
    pdf = PDF('L', 'mm', (250, 350))
    pdf.generate_pdf(prestamo_data)
    response.write(pdf.output(dest='S').encode('latin1'))
    return response


# ---------------------------------------------------------------------------------------------------------------------------#

@csrf_exempt
def GetFolioPrestamo(request):
    q=request.GET.get("q")
    queryset =DetallePrestamos.objects.filter(Q(pres_folio__pres_fecha_prestamo__year = '2022')).order_by('-pres_folio__pres_fechahora')
    if q and q !=" ":
        #q =q.split(" ")
        if q.isnumeric():
            query = (Q(pres_folio__pres_folio=q) | Q(vide_clave__vide_codigo=q )) 
        else:
            query = (Q(pres_folio__usua_clave__icontains=q) ) 
        queryset = queryset.filter(query)    

    #list = []  
    #for comp in querysetComp:
        #consulta=Compensaciones.objects.filter(Q(compensacion = comp))
       # list.append(CompToShow(comp.nombre + " (" + str(comp.numero -consulta.count()) +")", comp.pk ))    

    t = get_template('prestamos/folio_search.html')
    content = t.render(
    {
        'prestamos': queryset, 
        #'compensacion' : list,
          
    })
    return HttpResponse(content)

@csrf_exempt
def GetFolioDetail(request):
    id=request.POST.get("id").strip()
    detailPrestamo =DetallePrestamos.objects.get(pres_folio = id)
    #videoDetail = MaestroCintas.objects.get(video_id =detailPrestamo.vide_clave )
    # programaDetail = DetalleProgramas.objects.filter(video_cbarras=videoDetail.video_cbarras)
    t = get_template('prestamos/detalle_prestamos.html')
    content = t.render(
    {
        #'cintas': videoDetail, 
        'detalles' : detailPrestamo,
          
    })
    return HttpResponse(content)



@csrf_exempt      
def RegisterInVideoteca(request):
    # usuario = request.POST['matricula']
    # admin = request.user
    # from django.db import connections
    # cursor = connections['users'].cursor()
    # cursor.execute("select nombres, apellido1, apellido2, activo from people_person where matricula = '"+ usuario + "'")
    # row = cursor.fetchall()
    # print(row[0][3])    
    if request.method == 'POST':
        print(request.POST['codigoBarras'])
        now = datetime.datetime(2022, 12, 29, 00, 00, 00, 0) 
        #datetime.datetime.now()
        codigoBarras = request.POST['codigoBarras']
        try:
            error="Código no encontrado"
            maestroCinta = MaestroCintas.objects.get(pk = codigoBarras)
            error= "Busqueda en Maestro Cintas"
           
            error= "Busqueda en Videos"
            detallesPrestamo = DetallePrestamos.objects.filter( Q(vide_clave = maestroCinta.video_id) )
            #& Q(depr_estatus ='A')
            error= "No se encontro en Prestamos"
            if detallesPrestamo.count() > 0:
                detallePrestamo = detallesPrestamo.latest('pres_folio')
                prestamo = Prestamos.objects.get(pres_folio= detallePrestamo.pres_folio_id)
            else:
                print("Hay que revisar los registros de esté codigo de barras")
                registro_data={"error": True, "errorMessage":"Hay que revisar los registros de esté codigo de barras"}
                return JsonResponse(registro_data,safe=True)
            
            detallePrestamo.depr_estatus='I'
            detallePrestamo.pres_fecha_devolucion = now
            # detallePrestamo.usuario_devuelve = usuario
            detallePrestamo.usuario_recibe = 'M090077'
            detallePrestamo.save()
            maestroCinta.video_estatus='En Videoteca'
            maestroCinta.save()

            prestamosActivos = DetallePrestamos.objects.filter(Q(pres_folio_id = prestamo.pk) & Q(depr_estatus ='A'))
            if prestamosActivos.count == 0:
                #VALIDAR SI AUN HAY PRESTAMOS ACTIVOS 
                prestamo.pres_estatus ='I'
                prestamo.pres_fecha_devolucion = now
                prestamo.save()

            registro_data={"error":False,"errorMessage":"Registro Exitoso!"}
        except Exception as e:
            registro_data={"error":True,"errorMessage":"No se dio de alta correctamente el reingreso: "+ error}
           
    return JsonResponse(registro_data,safe=True)

@csrf_exempt  
def ValidateOutVideoteca(request):
    if request.method == 'POST':
        print(request.POST['codigoBarras'])
        codigoBarras = request.POST['codigoBarras']
        try:
            maestroCinta = MaestroCintas.objects.get(pk = codigoBarras)
            if maestroCinta.video_estatus =='En Videoteca':
                registro_data={"error":False,"errorMessage":"Listo para prestamo"}
            else:
                registro_data={"error":True,"errorMessage":"El material solicitado se encuentra registrado con estatus: " + maestroCinta.video_estatus}
        except Exception as e:
            registro_data={"error":True,"errorMessage":"No se encontro el codigo de barras"}    
    return JsonResponse(registro_data,safe=True)


@csrf_exempt      
def RegisterOutVideoteca(request):
    now = datetime.datetime.now()
    if request.method == 'POST':
        usuario = request.POST['usuario']
        data = json.loads(request.POST['codigos'])
        for codigo in data:
            maestroCinta = MaestroCintas.objects.get(pk = codigo)

            prestamo = Prestamos()
            prestamo.usua_clave = usuario
            prestamo.pres_fechahora = now
            prestamo.pres_fecha_prestamo = now
            prestamo.pres_fecha_devolucion = now
            prestamo.pres_estatus = 'X'
            prestamo.save()

            detPrestamos = DetallePrestamos()
            detPrestamos.pres_folio = prestamo
            # detPrestamos.vide_clave = videos
            detPrestamos.depr_estatus = 'X'
            detPrestamos.save()

            maestroCinta.video_estatus = 'X'
            maestroCinta.save()

        registro_data={"error":True,"errorMessage":"No se encontro el codigo de barras"}    
    return JsonResponse(registro_data,safe=True)
    