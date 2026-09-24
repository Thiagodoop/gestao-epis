import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def formatar_data_br(data_val):
    """Converte datas do banco (YYYY-MM-DD) para o padrão brasileiro (DD/MM/YYYY)."""
    if not data_val or data_val == "-":
        return "-"
    data_str = str(data_val).strip()[:10]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(data_str, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return data_str

def gerar_ficha_pdf(dados_funcionario, registros_entregas):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    elementos = []
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        name="TituloPDF",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#0f172a")
    )
    estilo_termo = ParagraphStyle(
        name="TermoNR6",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        alignment=4,
        textColor=colors.HexColor("#1e293b")
    )
    estilo_info_colab = ParagraphStyle(
        name="InfoColab",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )
    estilo_th = ParagraphStyle(
        name="HeaderTabela",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        alignment=1,
        textColor=colors.HexColor("#0f172a")
    )
    estilo_td = ParagraphStyle(
        name="CelulaTabela",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        alignment=1,
        textColor=colors.HexColor("#1e293b")
    )
    estilo_assinatura = ParagraphStyle(
        name="LinhaAssinatura",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#0f172a")
    )

    # 1. Cabeçalho
    elementos.append(Paragraph("<b>FICHA INDIVIDUAL DE CONTROLE E ENTREGA DE EPI</b>", estilo_titulo))
    elementos.append(Spacer(1, 10))

    # 2. Dados do Colaborador com Data de Admissão formatada
    nome = str(dados_funcionario[1]) if len(dados_funcionario) > 1 else "-"
    cpf = str(dados_funcionario[2]) if len(dados_funcionario) > 2 else "-"
    matricula = str(dados_funcionario[3]) if len(dados_funcionario) > 3 else "-"
    cargo = str(dados_funcionario[4]) if len(dados_funcionario) > 4 else "-"
    setor = str(dados_funcionario[5]) if len(dados_funcionario) > 5 else "-"
    data_adm_br = formatar_data_br(dados_funcionario[6]) if len(dados_funcionario) > 6 else "-"

    dados_colab = [
        [
            Paragraph(f"<b>Colaborador:</b> {nome}", estilo_info_colab),
            Paragraph(f"<b>CPF:</b> {cpf}", estilo_info_colab)
        ],
        [
            Paragraph(f"<b>Matrícula:</b> {matricula}", estilo_info_colab),
            Paragraph(f"<b>Cargo / Função:</b> {cargo}", estilo_info_colab)
        ],
        [
            Paragraph(f"<b>Setor:</b> {setor}", estilo_info_colab),
            Paragraph(f"<b>Data de Admissão:</b> {data_adm_br}", estilo_info_colab)
        ]
    ]

    tabela_colab = Table(dados_colab, colWidths=[340, 205])
    tabela_colab.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#94a3b8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabela_colab)
    elementos.append(Spacer(1, 8))

    # 3. Termo Legal NR-6
    termo = (
        "<b>TERMO DE RESPONSABILIDADE E COMPROMISSO (NR-6):</b> Declaro ter recebido da empresa, gratuitamente, os "
        "Equipamentos de Proteção Individual (EPIs) relacionados abaixo, novos ou em perfeitas condições de conservação "
        "e funcionamento, bem como as instruções e treinamento para sua adequada utilização, guarda e higienização. "
        "Comprometo-me a usá-los durante toda a jornada laboral apenas para as finalidades a que se destinam, comunicando "
        "qualquer alteração que os torne impróprios ao uso, ciente das obrigações do art. 158 da CLT e item 6.6.1 da NR-6."
    )
    elementos.append(Paragraph(termo, estilo_termo))
    elementos.append(Spacer(1, 8))

    # 4. Tabela de Registros com Datas formatadas
    cabecalho = [
        Paragraph("<b>Dt. Entrega</b>", estilo_th),
        Paragraph("<b>Descrição / C.A.</b>", estilo_th),
        Paragraph("<b>Qtd</b>", estilo_th),
        Paragraph("<b>Motivo Entrega</b>", estilo_th),
        Paragraph("<b>Assinatura Entrega</b>", estilo_th),
        Paragraph("<b>Dt. Devolução</b>", estilo_th),
        Paragraph("<b>Status / Motivo</b>", estilo_th)
    ]
    tabela_linhas = [cabecalho]

    for reg in registros_entregas:
        dt_e = formatar_data_br(reg[0]) if len(reg) > 0 and reg[0] else "-"
        nome_epi = str(reg[1]) if len(reg) > 1 and reg[1] else "EPI"
        ca = str(reg[2]) if len(reg) > 2 and reg[2] else "-"
        qtd = str(reg[3]) if len(reg) > 3 and reg[3] else "1"
        motivo_e = str(reg[4]) if len(reg) > 4 and reg[4] else "-"
        path_ass = reg[5] if len(reg) > 5 else None
        dt_d = formatar_data_br(reg[6]) if len(reg) > 6 and reg[6] else "-"
        motivo_d = str(reg[7]) if len(reg) > 7 and reg[7] else (str(reg[8]) if len(reg) > 8 and reg[8] else "Em Uso")

        desc_epi = f"{nome_epi}<br/><b>CA: {ca}</b>"

        img_ass = Paragraph("-", estilo_td)
        if path_ass and os.path.exists(path_ass):
            try:
                img_ass = RLImage(path_ass, width=55, height=18)
            except Exception:
                img_ass = Paragraph("Assinado", estilo_td)

        linha = [
            Paragraph(dt_e, estilo_td),
            Paragraph(desc_epi, estilo_td),
            Paragraph(qtd, estilo_td),
            Paragraph(motivo_e, estilo_td),
            img_ass,
            Paragraph(dt_d, estilo_td),
            Paragraph(motivo_d, estilo_td)
        ]
        tabela_linhas.append(linha)

    tabela_itens = Table(tabela_linhas, colWidths=[55, 140, 25, 85, 75, 55, 110])
    tabela_itens.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#64748b")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    elementos.append(tabela_itens)
    elementos.append(Spacer(1, 15))

    # 5. Encerramento com linha de assinatura e data
    secao_assinatura = [
        Spacer(1, 10),
        Paragraph("Declaro que as informações e registros constantes nesta ficha correspondem à realidade.", estilo_termo),
        Spacer(1, 25),
        Table([
            [
                Paragraph(f"____________________________________________________<br/><b>{nome}</b>", estilo_assinatura),
                Paragraph("______/______/____________<br/><b>Data de Emissão / Visto</b>", estilo_assinatura)
            ]
        ], colWidths=[370, 175], style=[
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    ]
    elementos.append(KeepTogether(secao_assinatura))

    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()