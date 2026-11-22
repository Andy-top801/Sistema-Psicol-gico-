# ==============================================================================
# MÓDULO: finanzas/pdf_utils.py
# DESCRIPCIÓN: Generación oficial de documentos financieros con ReportLab (PDF)
#              y OpenPyXL (Excel streaming write_only) para HU-52 y HU-54:
#              - Recibo oficial de cobro en Bs.
#              - Extracto histórico tipo bancario multipágina (hasta 20 años)
#              - Boleta oficial de liquidación de honorarios a psicólogos
# ==============================================================================
import csv
import io
from datetime import datetime
from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas

import openpyxl


COLOR_PRIMARY_DARK = colors.HexColor('#0F2922')
COLOR_PRIMARY = colors.HexColor('#0D9488')
COLOR_LIGHT_BG = colors.HexColor('#F0FDFA')
COLOR_ZEBRA = colors.HexColor('#F8FAFC')
COLOR_BORDER = colors.HexColor('#CBD5E1')
COLOR_TEXT = colors.HexColor('#0F172A')


class NumberedCanvas(canvas.Canvas):
    """Canvas con numeración automática 'Página X de Y' para reportes multipágina."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(num_pages)
            super().showPage()
        super().save()

    def _draw_page_number(self, page_count):
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#64748B'))
        width = self._pagesize[0]
        self.drawRightString(width - 36, 20, f"Página {self._pageNumber} de {page_count}")
        self.drawString(36, 20, "SIGEPSI — Documento Financiero Oficial (BOB Bs.)")


def generar_recibo_pago_pdf(pago, tenant_name: str = 'Centro Psicológico') -> HttpResponse:
    """HU-52: Comprobante oficial de cobro en Bolivianos (Bs.)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('ReciboTitle', parent=styles['Heading1'], fontSize=16, textColor=COLOR_PRIMARY_DARK, spaceAfter=4)
    sub_style = ParagraphStyle('ReciboSub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=14)

    pac = pago.cuenta.paciente
    pac_nombre = f"{pac.usuario.nombre} {pac.usuario.apellido}".strip()
    psico_nombre = 'N/A'
    fecha_cita = 'N/A'
    if pago.cita:
        psico_nombre = f"Lic. {pago.cita.psicologo.usuario.nombre} {pago.cita.psicologo.usuario.apellido}".strip()
        fecha_cita = f"{pago.cita.fecha.isoformat()} {pago.cita.hora_inicio.strftime('%H:%M')}"

    cajero = f"{pago.registrado_por.nombre} {pago.registrado_por.apellido}".strip() if pago.registrado_por else 'Sistema'
    fecha_pago_str = timezone.localtime(pago.fecha_pago).strftime('%d/%m/%Y %H:%M:%S')

    story = [
        Paragraph(f"RECIBO OFICIAL DE PAGO — {tenant_name.upper()}", title_style),
        Paragraph(f"N° Recibo: <b>{pago.numero_recibo}</b> &nbsp;|&nbsp; Código Verificación: <b>{pago.codigo_verificacion}</b>", sub_style),
    ]

    datos_tabla = [
        ['Campo', 'Detalle'],
        ['Fecha y Hora de Pago', fecha_pago_str],
        ['Paciente', f"{pac_nombre} (Expediente: {pac.codigo_expediente})"],
        ['Psicólogo / Servicio', f"{psico_nombre} — Cita: {fecha_cita}"],
        ['Método de Pago', pago.get_metodo_pago_display()],
        ['Referencia Externa', pago.referencia_externa or '-'],
        ['Monto Pagado', f"Bs. {pago.monto:,.2f}"],
        ['Saldo Pendiente Actual', f"Bs. {pago.cuenta.saldo_pendiente:,.2f}"],
        ['Registrado Por', cajero],
        ['Observaciones', pago.observaciones or '-'],
    ]

    table = Table(datos_tabla, colWidths=[2.3 * inch, 4.8 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_ZEBRA]),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 6), (-1, 6), COLOR_LIGHT_BG),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"Comprobante generado electrónicamente por SIGEPSI. Código de integridad: <b>{pago.codigo_verificacion}</b>.",
        ParagraphStyle('Foot', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor('#64748B')),
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_{pago.numero_recibo}.pdf"'
    return response


def generar_extracto_bancario_pdf(meta: dict, rows_iter, tenant_name: str = 'Centro Psicológico') -> HttpResponse:
    """
    HU-52: Extracto Histórico de Pagos tipo Bancario multipágina (hasta 20 años)
    con encabezados repetidos por página, subtotales anuales y saldo acumulado.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=28,
        leftMargin=28,
        topMargin=32,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ExtTitle', parent=styles['Heading1'], fontSize=14, textColor=COLOR_PRIMARY_DARK, spaceAfter=4)
    meta_style = ParagraphStyle('ExtMeta', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#334155'), spaceAfter=10)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=7.5, leading=9.5, textColor=COLOR_TEXT)

    story = [
        Paragraph(f"EXTRACTO HISTÓRICO DE PAGOS (TIPO BANCARIO) — {tenant_name.upper()}", title_style),
        Paragraph(
            f"Titular / Alcance: <b>{meta['paciente_label']}</b> &nbsp;|&nbsp; "
            f"Periodo: <b>{meta['fecha_desde']}</b> al <b>{meta['fecha_hasta']}</b> &nbsp;|&nbsp; "
            f"Movimientos: <b>{meta['total_registros']}</b> &nbsp;|&nbsp; Moneda: <b>Bs. (BOB)</b>",
            meta_style,
        ),
    ]

    # Resumen superior tipo extracto bancario
    resumen_data = [[
        f"Saldo Inicial:\nBs. {meta['saldo_inicial']:,.2f}",
        f"Total Cargos (Debe):\nBs. {meta['total_debe']:,.2f}",
        f"Total Pagos (Haber):\nBs. {meta['total_haber']:,.2f}",
        f"Saldo Final:\nBs. {meta['saldo_final']:,.2f}",
    ]]
    res_table = Table(resumen_data, colWidths=[2.55 * inch] * 4)
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.8, COLOR_PRIMARY),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(res_table)
    story.append(Spacer(1, 12))

    # Tabla de movimientos cronológicos con encabezados repetidos por página
    headers = ['Fecha', 'Expediente / Paciente', 'Documento', 'Concepto', 'Método', 'Debe (Bs.)', 'Haber (Bs.)', 'Saldo (Bs.)']
    table_data = [headers]
    for r in rows_iter:
        table_data.append([
            r['fecha'],
            Paragraph(f"<b>{r['expediente']}</b><br/>{r['paciente']}", cell_style),
            r['documento'],
            Paragraph(r['concepto'], cell_style),
            r['metodo_pago'],
            f"{r['debe']:,.2f}" if r['debe'] else '-',
            f"{r['haber']:,.2f}" if r['haber'] else '-',
            f"{r['saldo_acumulado']:,.2f}",
        ])

    if len(table_data) == 1:
        table_data.append(['-', 'Sin movimientos en el periodo', '-', '-', '-', '0.00', '0.00', f"{meta['saldo_inicial']:,.2f}"])

    col_widths = [1.05 * inch, 1.55 * inch, 1.15 * inch, 2.55 * inch, 0.90 * inch, 0.95 * inch, 0.95 * inch, 1.05 * inch]
    mov_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    mov_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_ZEBRA]),
        ('GRID', (0, 0), (-1, -1), 0.35, COLOR_BORDER),
        ('ALIGN', (5, 1), (7, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(mov_table)

    # Resumen anual al final del extracto
    if meta.get('resumen_anual'):
        story.append(Spacer(1, 14))
        story.append(Paragraph("Resumen Consolidado por Año", styles['Heading3']))
        anual_rows = [['Año', 'Movimientos', 'Total Debe (Bs.)', 'Total Haber (Bs.)', 'Variación Neta (Bs.)']]
        for a in meta['resumen_anual']:
            anual_rows.append([
                str(a['anio']),
                str(a['movimientos']),
                f"{a['total_debe']:,.2f}",
                f"{a['total_haber']:,.2f}",
                f"{a['variacion_neta']:,.2f}",
            ])
        anual_table = Table(anual_rows, colWidths=[1.2 * inch, 1.4 * inch, 2.0 * inch, 2.0 * inch, 2.0 * inch], repeatRows=1)
        anual_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.4, COLOR_BORDER),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_ZEBRA]),
        ]))
        story.append(anual_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    filename = f"extracto_pagos_{meta['fecha_desde']}_{meta['fecha_hasta']}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def generar_extracto_bancario_excel(meta: dict, rows_iter, tenant_name: str = 'Centro Psicológico') -> HttpResponse:
    """
    HU-52: Exportación Excel en modo write_only (streaming) para soportar
    extractos históricos de hasta 20 años con miles de filas sin saturar RAM.
    """
    wb = openpyxl.Workbook(write_only=True)

    ws = wb.create_sheet(title='Extracto Histórico')
    ws.append([f"SIGEPSI — EXTRACTO HISTÓRICO DE PAGOS — {tenant_name.upper()}"])
    ws.append([
        f"Titular: {meta['paciente_label']}",
        f"Periodo: {meta['fecha_desde']} a {meta['fecha_hasta']}",
        f"Saldo Inicial (Bs.): {meta['saldo_inicial']:.2f}",
        f"Saldo Final (Bs.): {meta['saldo_final']:.2f}",
    ])
    ws.append([])
    ws.append(['Fecha', 'Expediente', 'Paciente', 'Tipo', 'N° Documento', 'Concepto', 'Método de Pago', 'Debe (Bs.)', 'Haber (Bs.)', 'Saldo Acumulado (Bs.)'])

    for r in rows_iter:
        ws.append([
            r['fecha'],
            r['expediente'],
            r['paciente'],
            r['tipo'],
            r['documento'],
            r['concepto'],
            r['metodo_pago'],
            r['debe'],
            r['haber'],
            r['saldo_acumulado'],
        ])

    ws_anual = wb.create_sheet(title='Resumen Anual')
    ws_anual.append(['Año', 'Movimientos', 'Total Debe (Bs.)', 'Total Haber (Bs.)', 'Variación Neta (Bs.)'])
    for a in meta.get('resumen_anual', []):
        ws_anual.append([a['anio'], a['movimientos'], a['total_debe'], a['total_haber'], a['variacion_neta']])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = f"extracto_pagos_{meta['fecha_desde']}_{meta['fecha_hasta']}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def generar_extracto_bancario_csv(meta: dict, rows_iter) -> StreamingHttpResponse:
    """HU-52: Exportación CSV en streaming para extractos masivos."""
    class Echo:
        def write(self, value):
            return value

    def _stream():
        writer = csv.writer(Echo())
        yield writer.writerow(['Fecha', 'Expediente', 'Paciente', 'Tipo', 'N° Documento', 'Concepto', 'Método de Pago', 'Debe (Bs.)', 'Haber (Bs.)', 'Saldo Acumulado (Bs.)'])
        for r in rows_iter:
            yield writer.writerow([
                r['fecha'], r['expediente'], r['paciente'], r['tipo'], r['documento'],
                r['concepto'], r['metodo_pago'], f"{r['debe']:.2f}", f"{r['haber']:.2f}", f"{r['saldo_acumulado']:.2f}",
            ])

    filename = f"extracto_pagos_{meta['fecha_desde']}_{meta['fecha_hasta']}.csv"
    response = StreamingHttpResponse(_stream(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def generar_boleta_liquidacion_pdf(liquidacion, tenant_name: str = 'Centro Psicológico') -> HttpResponse:
    """HU-54: Boleta oficial de liquidación de honorarios profesionales en Bs."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=40)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('LiqTitle', parent=styles['Heading1'], fontSize=15, textColor=COLOR_PRIMARY_DARK, spaceAfter=4)
    sub_style = ParagraphStyle('LiqSub', parent=styles['Normal'], fontSize=9.5, textColor=colors.HexColor('#475569'), spaceAfter=12)

    psico = liquidacion.psicologo
    psico_nom = f"Lic. {psico.usuario.nombre} {psico.usuario.apellido}".strip()

    story = [
        Paragraph(f"BOLETA DE LIQUIDACIÓN DE HONORARIOS — {tenant_name.upper()}", title_style),
        Paragraph(
            f"Código: <b>{liquidacion.codigo_liquidacion}</b> &nbsp;|&nbsp; Estado: <b>{liquidacion.estado}</b> &nbsp;|&nbsp; "
            f"Periodo: <b>{liquidacion.fecha_inicio.isoformat()}</b> al <b>{liquidacion.fecha_fin.isoformat()}</b>",
            sub_style,
        ),
    ]

    pct_psico = 100 - float(liquidacion.porcentaje_comision_centro)
    resumen = [
        ['Profesional', psico_nom, 'N° Colegiado', psico.numero_colegiado or '-'],
        ['Total Sesiones', str(liquidacion.total_sesiones), 'Reparto', f"{pct_psico:.0f}% Psicólogo / {float(liquidacion.porcentaje_comision_centro):.0f}% Centro"],
        ['Monto Bruto', f"Bs. {liquidacion.monto_bruto:,.2f}", 'Retención Centro', f"Bs. {liquidacion.comision_centro:,.2f}"],
        ['Neto a Pagar', f"Bs. {liquidacion.monto_neto_psicologo:,.2f}", 'Ref. Bancaria', liquidacion.referencia_bancaria or 'Pendiente'],
    ]
    res_tbl = Table(resumen, colWidths=[1.4 * inch, 2.2 * inch, 1.4 * inch, 2.2 * inch])
    res_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLOR_ZEBRA),
        ('BACKGROUND', (2, 0), (2, -1), COLOR_ZEBRA),
        ('BACKGROUND', (0, 3), (1, 3), COLOR_LIGHT_BG),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(res_tbl)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Detalle de Sesiones Realizadas Liquidadas", styles['Heading3']))
    det_rows = [['Fecha', 'Paciente', 'Modalidad', 'Bruto (Bs.)', 'Comisión (Bs.)', 'Neto (Bs.)']]
    for d in liquidacion.detalles.select_related('cita__paciente__usuario').order_by('cita__fecha', 'cita__hora_inicio'):
        pac_u = d.cita.paciente.usuario
        det_rows.append([
            d.cita.fecha.isoformat(),
            f"{pac_u.nombre} {pac_u.apellido}".strip(),
            d.cita.modalidad,
            f"{d.monto_sesion:,.2f}",
            f"{d.comision_sesion:,.2f}",
            f"{d.neto_sesion:,.2f}",
        ])

    det_tbl = Table(det_rows, colWidths=[1.0 * inch, 2.3 * inch, 1.0 * inch, 0.95 * inch, 0.95 * inch, 1.0 * inch], repeatRows=1)
    det_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_ZEBRA]),
        ('GRID', (0, 0), (-1, -1), 0.4, COLOR_BORDER),
        ('ALIGN', (3, 1), (5, -1), 'RIGHT'),
    ]))
    story.append(det_tbl)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleta_{liquidacion.codigo_liquidacion}.pdf"'
    return response
