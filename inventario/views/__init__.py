
from .maestrocintas import login, DetalleProgramasDeleteView, DetalleProgramasUpdateView, DetalleProgramasCreateView, DetalleProgramasDetailView, DetalleProgramasCreateView, DetalleProgramasUpdateView, DetalleProgramasDetailView, DetalleProgramasCreateView, DetalleProgramasListView, MaestroCintasFormView, MaestroCintasDeleteView, MaestroCintasUpdateView, MaestroCintasDetailView, MaestroCintasCreateView, MaestroCintasListView, FormatosCintasCreateView, FormatosCintasDetailView, FormatosCintasListView, FormatosCintasFormView
from .prestamos import PrestamosListView, GetFolioPrestamo, GetFolioDetail, RegisterInVideoteca, ValidateOutVideoteca, RegisterOutVideoteca,PrestamoDetalle, Filtrar_prestamos, EndInVideoteca
from .reports import generar_pdf, generar_pdf_modal