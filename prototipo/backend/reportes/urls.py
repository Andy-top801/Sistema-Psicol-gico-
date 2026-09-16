from django.urls import path
from .views import (
    ReporteMetadataView,
    ReporteGenericoView,
    ReportePersonalizadoView,
    ReporteExportCSVView,
    ReporteExportExcelView,
    ReporteExportHTMLView,
    ReporteEmailView,
)

urlpatterns = [
    path('metadata/', ReporteMetadataView.as_view(), name='reporte-metadata'),
    path('personalizado/', ReportePersonalizadoView.as_view(), name='reporte-personalizado'),
    path('email/', ReporteEmailView.as_view(), name='reporte-email'),
    path('<str:fuente>/export/excel/', ReporteExportExcelView.as_view(), name='reporte-export-excel'),
    path('<str:fuente>/export/csv/', ReporteExportCSVView.as_view(), name='reporte-export-csv'),
    path('<str:fuente>/export/html/', ReporteExportHTMLView.as_view(), name='reporte-export-html'),
    path('<str:fuente>/', ReporteGenericoView.as_view(), name='reporte-generico'),
]
