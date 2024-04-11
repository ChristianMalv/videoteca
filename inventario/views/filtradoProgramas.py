from django.shortcuts import render
from..models import ProgramaSeries, MaestroCintas, RegistroCalificacion
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Value, CharField

@csrf_exempt
def filtrarBusqueda(request):
    if request.method == 'GET':
        serie = request.GET.get('serie', '').lower()
        subtituloSerie = request.GET.get('subtituloSerie', '').lower()
        programa = request.GET.get('programa', '').lower()
        subtituloPrograma = request.GET.get('subtituloPrograma', '').lower()
        codigo_barras = request.GET.get('codigo_barras', '').lower()
        sinopsis = request.GET.get('sinopsis', '').lower()

        # Inicializar cat_status con un valor predeterminado
        cat_status = None

        # Filtrar ProgramaSeries
        resultados_programaseries = ProgramaSeries.objects.filter(
            serie__unaccent__icontains=serie,
            subtituloSerie__unaccent__icontains=subtituloSerie,
            programa__unaccent__icontains=programa,
            subtituloPrograma__unaccent__icontains=subtituloPrograma,
            codigo_barras__video_cbarras__unaccent__icontains=codigo_barras,
            sinopsis__unaccent__icontains=sinopsis
        )

        # Combinar resultados de ambas tablas
        data = []
        if resultados_programaseries.exists():
            for resultado in resultados_programaseries:
                try:
                    maestro_cintas = MaestroCintas.objects.get(video_cbarras=resultado.codigo_barras_id)
                    cat_status = maestro_cintas.video_tipo

                    data.append({
                        'codigo_barras': resultado.codigo_barras.video_cbarras,
                        'serie': resultado.serie,
                        'programa': resultado.programa,
                        'subtituloPrograma': resultado.subtituloPrograma,
                        'tipo': cat_status.status,
                        'estatus': maestro_cintas.video_estatus
                    })
                except MaestroCintas.DoesNotExist:
                    print(f"MaestroCintas not found for video_cbarras: {resultado.codigo_barras_id}")
        else:
            # Filtrar RegistroCalificacion si no hay resultados en ProgramaSeries
            resultados_registro_calificacion = RegistroCalificacion.objects.filter(
                serie__unaccent__icontains=serie,
                programa__unaccent__icontains=programa,
                subtitulo_programa__unaccent__icontains=subtituloPrograma,
                codigo_barras__video_cbarras__unaccent__icontains=codigo_barras,
                sinopsis__unaccent__icontains=sinopsis
            )

            for resultado in resultados_registro_calificacion:
                try:
                    maestro_cintas = MaestroCintas.objects.get(video_cbarras=resultado.codigo_barras_id)
                    cat_status = maestro_cintas.video_tipo

                    data.append({
                        'codigo_barras': resultado.codigo_barras.video_cbarras,
                        'serie': resultado.serie,
                        'programa': resultado.programa,
                        'subtituloPrograma': resultado.subtitulo_programa,
                        'tipo': cat_status.status,
                        'estatus': maestro_cintas.video_estatus
                    })
                except MaestroCintas.DoesNotExist:
                    print(f"MaestroCintas not found for video_cbarras: {resultado.codigo_barras_id}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'data': data}, safe=False)
        else:
            return render(request, 'calificaForm/filtrarBusqueda.html', {'data': data})