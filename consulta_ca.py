import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def extrair_campo_linear(linhas, rotulos_alvo):
    """
    Percorre a lista ordenada de linhas de texto da página.
    Ao encontrar o rótulo exato, pega a linha subsequente válida.
    """
    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        for rotulo in rotulos_alvo:
            # Encontra rótulo exato ou seguido de dois pontos
            if re.match(rf"^{re.escape(rotulo)}\s*:?$", linha_limpa, re.IGNORECASE):
                # Procura a primeira linha abaixo que não seja vazia nem outro rótulo
                for j in range(i + 1, min(i + 5, len(linhas))):
                    candidato = linhas[j].strip()
                    if candidato and not any(re.match(rf"^{re.escape(r)}\s*:?$", candidato, re.IGNORECASE) for r in [
                        "Razão Social", "CNPJ", "Nome Fantasia", "Site", "Cidade/UF", 
                        "Avaliação Geral", "Marcação", "Referências", "Aprovado Para", 
                        "Laudos", "N° do Laudo", "CNPJ do Laboratório", "Normas", "Descrição Completa"
                    ]):
                        return candidato
    return ""

def consultar_dados_ca(numero_ca):
    numero_ca = str(numero_ca).strip()
    if not numero_ca.isdigit():
        return {"sucesso": False, "mensagem": "O número do CA deve conter apenas dígitos numéricos."}

    url = f"https://consultaca.com/{numero_ca}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=12)
        
        if response.status_code == 404:
            return {"sucesso": False, "mensagem": f"CA nº {numero_ca} não foi localizado."}
            
        if response.status_code != 200:
            return {"sucesso": False, "mensagem": f"Erro de conexão com o portal (Código {response.status_code})."}

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove scripts, estilos e ícones
        for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
            tag.decompose()

        # Extrai todas as linhas de texto em sequência estrita
        linhas = [re.sub(r'\s+', ' ', l).strip() for l in soup.get_text("\n").split("\n")]
        linhas = [l for l in linhas if l]
        texto_geral = "\n".join(linhas)

        # 1. Título do Equipamento
        h1 = soup.find("h1")
        equipamento = h1.get_text(strip=True) if h1 else f"EPI - CA {numero_ca}"
        equipamento = re.sub(r"^CA\s*\d+\s*-\s*", "", equipamento, flags=re.IGNORECASE).strip()

        # 2. Situação e Validade
        situacao = "VÁLIDO"
        if re.search(r"Situação\s*[:\n\r]*VENCIDO", texto_geral, re.IGNORECASE) or "venceu há" in texto_geral.lower():
            situacao = "VENCIDO"

        validade = ""
        validade_iso = None
        m_val = re.search(r"Validade\s*[:\n\r]*(\d{2}/\d{2}/\d{4})", texto_geral, re.IGNORECASE)
        if not m_val:
            m_val = re.search(r"(\d{2}/\d{2}/\d{4})", texto_geral)
        if m_val:
            validade = m_val.group(1)
            try:
                dt = datetime.strptime(validade, "%d/%m/%Y")
                validade_iso = dt.strftime("%Y-%m-%d")
            except Exception:
                pass

        # 3. Processo e Natureza
        processo = ""
        m_proc = re.search(r"(?:N[ºo°]?\s*Processo|Processo)\s*[:\n\r]*([0-9\.\-/]+)", texto_geral, re.IGNORECASE)
        if m_proc:
            processo = m_proc.group(1).strip()

        natureza = extrair_campo_linear(linhas, ["Natureza"])
        if not natureza or len(natureza) > 30:
            natureza = "Nacional" if "Nacional" in texto_geral else "Importado"

        # 4. Descrição Completa
        descricao_completa = ""
        m_desc = re.search(r"Descrição Completa\s*\n+(.*?)(?=\n+Fabricante|\n+Razão Social|\n+Dados Complementares)", texto_geral, re.DOTALL | re.IGNORECASE)
        if m_desc:
            descricao_completa = re.sub(r'\s+', ' ', m_desc.group(1)).strip()

        # 5. Fabricante
        # Procura a Razão Social que vem logo abaixo de Fabricante
        razao_social = ""
        for i, l in enumerate(linhas):
            if l.lower() == "fabricante":
                # A partir daqui, pega o próximo "Razão Social"
                sublinhas = linhas[i:i+15]
                razao_social = extrair_campo_linear(sublinhas, ["Razão Social"])
                break
        if not razao_social:
            razao_social = extrair_campo_linear(linhas, ["Razão Social"])

        # CNPJ do Fabricante (primeiro CNPJ que aparece no texto)
        cnpjs_encontrados = re.findall(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", texto_geral)
        cnpj = cnpjs_encontrados[0] if cnpjs_encontrados else ""

        nome_fantasia = extrair_campo_linear(linhas, ["Nome Fantasia"])
        
        # Site (captura URL limpa)
        site = ""
        m_site = re.search(r"(https?://[^\s]+|www\.[^\s]+)", texto_geral)
        if m_site:
            site = m_site.group(1).rstrip("/.")

        cidade_uf = extrair_campo_linear(linhas, ["Cidade/UF"])
        if not cidade_uf or "/" not in cidade_uf:
            m_cidade = re.search(r"([A-ZÁ-Úa-zá-ú\s]+/[A-Z]{2})", texto_geral)
            if m_cidade:
                cidade_uf = m_cidade.group(1).strip()

        avaliacao_geral = extrair_campo_linear(linhas, ["Avaliação Geral"])
        
        total_cas_fabricante = ""
        m_total = re.search(r"Total de CA['’]?s?\s*(?:do Fabricante)?\s*[:\s]*(\d+)", texto_geral, re.IGNORECASE)
        if m_total:
            total_cas_fabricante = m_total.group(1)

        # 6. Dados Complementares
        marcacao = extrair_campo_linear(linhas, ["Marcação", "Marcação do CA"])
        referencias = extrair_campo_linear(linhas, ["Referências", "Referência"])
        aprovado_para = extrair_campo_linear(linhas, ["Aprovado Para", "Aprovado para"])

        # 7. Laudos e Laboratório
        num_laudo = extrair_campo_linear(linhas, ["N° do Laudo", "Nº do Laudo", "Laudo"])
        
        # CNPJ do Laboratório (é o segundo CNPJ da página)
        cnpj_laboratorio = cnpjs_encontrados[1] if len(cnpjs_encontrados) > 1 else ""

        # Razão Social do Laboratório
        razao_laboratorio = ""
        for i, l in enumerate(linhas):
            if "laudos" in l.lower() or "cnpj do laboratório" in l.lower():
                sublinhas = linhas[i:i+15]
                razao_laboratorio = extrair_campo_linear(sublinhas, ["Razão Social"])
                break

        # 8. Normas Técnicas
        normas = list(set(re.findall(r"(?:ABNT\s+NBR(?:\s+ISO)?\s+\d+[\:\-]?\d*|ISO\s+\d+[\:\-]?\d*|EN\s+\d+[\:\-]?\d*)", texto_geral, re.IGNORECASE)))
        normas.sort()

        return {
            "sucesso": True,
            "ca": numero_ca,
            "equipamento": equipamento,
            "situacao": situacao,
            "validade": validade,
            "validade_iso": validade_iso,
            "processo": processo,
            "natureza": natureza,
            "descricao_completa": descricao_completa,
            "razao_social": razao_social,
            "cnpj": cnpj,
            "nome_fantasia": nome_fantasia,
            "site": site,
            "cidade_uf": cidade_uf,
            "avaliacao_geral": avaliacao_geral,
            "total_cas_fabricante": total_cas_fabricante,
            "marcacao": marcacao,
            "referencias": referencias,
            "aprovado_para": aprovado_para,
            "num_laudo": num_laudo,
            "cnpj_laboratorio": cnpj_laboratorio,
            "razao_laboratorio": razao_laboratorio,
            "normas": normas
        }

    except requests.exceptions.RequestException:
        return {"sucesso": False, "mensagem": "Falha na conexão com o site consultaca.com."}