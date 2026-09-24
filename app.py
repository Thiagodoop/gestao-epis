import streamlit as st
import sqlite3
import os
import zipfile
import io
from datetime import datetime
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from gerador_pdf import gerar_ficha_pdf
from consulta_ca import consultar_dados_ca

# Configuração da página
st.set_page_config(
    page_title="Gestão de EPIs | NR-6", 
    layout="wide", 
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS PERSONALIZADO: CONTRASTE TOTAL EM BOTÕES, DATAS E CAMPOS
# =========================================================
st.markdown("""
<style>
    /* 1. FUNDO GERAL DA APLICAÇÃO (Bege Claro -> Letras Escuras) */
    .stApp {
        background-color: #EFE6D6 !important;
        color: #1F2E3A !important;
    }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp label {
        color: #1F2E3A !important;
    }

    /* 2. BARRA LATERAL (Fundo Escuro #1F2E3A -> Letras Brancas) */
    [data-testid="stSidebar"] {
        background-color: #1F2E3A !important;
        border-right: 2px solid #D8C7A8 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* Caixinhas Visíveis do Menu Lateral */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 2px solid #D8C7A8 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 0.65rem 0.9rem !important;
        margin-bottom: 0.35rem !important;
        text-align: left !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        display: block !important;
    }
    [data-testid="stSidebar"] .stButton > button * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #D8C7A8 !important;
        border-color: #FFFFFF !important;
        transform: translateX(3px);
    }
    [data-testid="stSidebar"] .stButton > button:hover * {
        color: #1F2E3A !important;
    }

    /* Caixinha Ativa no Menu Lateral */
    [data-testid="stSidebar"] .btn-menu-ativo > button {
        background-color: #D8C7A8 !important;
        border: 2px solid #FFFFFF !important;
    }
    [data-testid="stSidebar"] .btn-menu-ativo > button * {
        color: #1F2E3A !important;
        font-weight: 900 !important;
    }

    /* 3. TODOS OS BOTÕES DA TELA PRINCIPAL (Fundo Azul -> Letras 100% Brancas) */
    .stApp button,
    .stApp [data-testid="stFormSubmitButton"] > button,
    .stApp [data-testid="stBaseButton-secondary"],
    .stApp [data-testid="stBaseButton-primary"],
    .stApp .stDownloadButton > button {
        background-color: #1F2E3A !important;
        border: 2px solid #1F2E3A !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 3px 6px rgba(31, 46, 58, 0.15) !important;
    }
    .stApp button *,
    .stApp [data-testid="stFormSubmitButton"] > button *,
    .stApp [data-testid="stBaseButton-secondary"] *,
    .stApp [data-testid="stBaseButton-primary"] *,
    .stApp .stDownloadButton > button * {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
    }
    .stApp button:hover,
    .stApp [data-testid="stFormSubmitButton"] > button:hover,
    .stApp .stDownloadButton > button:hover {
        background-color: #D8C7A8 !important;
        border-color: #1F2E3A !important;
    }
    .stApp button:hover *,
    .stApp [data-testid="stFormSubmitButton"] > button:hover *,
    .stApp .stDownloadButton > button:hover * {
        color: #1F2E3A !important;
    }

    /* 4. CORREÇÃO ESPECÍFICA DO REACT-ARIA DATE INPUT (DIA, MÊS, ANO E BARRAS) */
    div[data-testid="stDateInput"] div[data-baseweb="input"],
    div[data-testid="stDateInput"] div[role="group"],
    div[data-testid="stDateInput"] [data-rac] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #D8C7A8 !important;
        border-radius: 8px !important;
    }

    /* Remove contornos internos ao clicar ou focar no dia, mês ou ano */
    div[data-testid="stDateInput"] span[role="spinbutton"],
    div[data-testid="stDateInput"] [data-rac] span,
    div[data-testid="stDateInput"] span:focus,
    div[data-testid="stDateInput"] [data-focused] {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Força os números (dia, mês, ano) e as barras de separação a ficarem nítidos */
    div[data-testid="stDateInput"] span[role="spinbutton"],
    div[data-testid="stDateInput"] span[data-type="day"],
    div[data-testid="stDateInput"] span[data-type="month"],
    div[data-testid="stDateInput"] span[data-type="year"],
    div[data-testid="stDateInput"] span[aria-hidden="true"],
    div[data-testid="stDateInput"] [data-rac] span {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        opacity: 1 !important;
        visibility: visible !important;
        text-shadow: none !important;
    }

    /* Ícone do calendário do st.date_input */
    div[data-testid="stDateInput"] svg {
        fill: #1F2E3A !important;
        color: #1F2E3A !important;
    }

    /* 5. DEMAIS CAMPOS DE ENTRADA (Texto, Área, Selectbox) */
    .stTextInput input, 
    .stTextArea textarea, 
    .stSelectbox select,
    .stNumberInput input {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border: 1.5px solid #D8C7A8 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    /* Rótulos dos formulários */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label, .stTextArea label, .stCheckbox label span {
        color: #1F2E3A !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
    }

    /* 6. CARDS DE MÉTRICAS */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 2px solid #D8C7A8 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 6px rgba(31, 46, 58, 0.08) !important;
    }
    [data-testid="stMetricValue"] * {
        color: #1F2E3A !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
    }
    [data-testid="stMetricLabel"] * {
        color: #1F2E3A !important;
        font-size: 0.95rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] div {
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        color: #15803D !important;
    }

    /* 7. ABAS SUPERIORES (Tabs) */
    button[data-baseweb="tab"] div {
        color: #475569 !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div {
        color: #1F2E3A !important;
        font-weight: 900 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: #1F2E3A !important;
        border-bottom-width: 3px !important;
    }

    /* 8. TABELAS (st.dataframe) */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border: 2px solid #D8C7A8 !important;
        border-radius: 8px !important;
    }

    /* 9. RODAPÉ */
    .footer-assinatura {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        color: #475569;
        font-size: 0.85rem;
        border-top: 1.5px dashed #D8C7A8;
        margin-top: 3rem;
    }
    .footer-assinatura b {
        color: #1F2E3A;
    }
</style>
""", unsafe_allow_html=True)

def get_connection():
    return sqlite3.connect("gestao_epi.db")

def formatar_data_br(data_val):
    if not data_val or str(data_val).strip() in ("-", "None", ""):
        return "-"
    data_str = str(data_val).strip()[:10]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(data_str, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return data_str

if not os.path.exists("assinaturas"):
    os.makedirs("assinaturas")

# Controle de Menu Lateral
if "menu_ativo" not in st.session_state:
    st.session_state.menu_ativo = "Dashboard Gerencial"

def trocar_menu(nome):
    st.session_state.menu_ativo = nome

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #FFFFFF;'>🛡️ Gestão de EPIs</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFFFFF; font-size: 0.85rem;'>Conformidade NR-6 & Estoque</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255, 255, 255, 0.35); margin: 0.8rem 0;'>", unsafe_allow_html=True)

    opcoes_menu = [
        ("📊 Dashboard Gerencial", "Dashboard Gerencial"),
        ("✍️ Registrar Entrega", "Registrar Entrega de EPI"),
        ("🔄 Devolução de EPI", "Devolução de EPI"),
        ("🎯 Matriz por Cargo", "Matriz de EPI por Cargo"),
        ("👤 Colaboradores", "Cadastrar Funcionário"),
        ("📦 Estoque de EPIs", "Estoque de EPIs"),
        ("📋 Ficha Individual", "Histórico / Ficha de EPI"),
        ("💾 Backup do Sistema", "Backup & Segurança")
    ]

    for label, chave in opcoes_menu:
        ativo = (st.session_state.menu_ativo == chave)
        css_classe = "btn-menu-ativo" if ativo else ""
        st.markdown(f"<div class='{css_classe}'>", unsafe_allow_html=True)
        if st.button(label, key=f"btn_nav_{chave}", use_container_width=True):
            trocar_menu(chave)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center; font-size: 0.85rem; color: #FFFFFF;'>"
        "Criador:<br><b style='color: #FFFFFF; font-size: 1rem;'>Thiago Soares da Rocha</b>"
        "</div>", 
        unsafe_allow_html=True
    )

menu = st.session_state.menu_ativo

# ==========================================
# 0. DASHBOARD GERENCIAL
# ==========================================
if menu == "Dashboard Gerencial":
    st.title("📊 Painel de Controle e Indicadores")
    st.caption("Visão consolidada de inventário, conformidade de C.A. e movimentações em tempo real.")

    hoje = datetime.now().date()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, ca, quantidade, estoque_minimo, validade_ca FROM epis")
    todos_epis = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE status='Ativo'")
    total_colab_ativos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM entregas WHERE COALESCE(status_item, 'Em Uso') = 'Em Uso'")
    total_epis_em_uso = cursor.fetchone()[0]
    conn.close()

    total_cadastrados = len(todos_epis)
    saldo_total_unidades = sum(e[3] for e in todos_epis)
    itens_alerta_estoque = []
    cas_vencidos = []
    cas_a_vencer = []

    for e in todos_epis:
        epi_id, nome, ca, qtd, est_min, val_ca_raw = e
        if qtd <= est_min:
            itens_alerta_estoque.append({"EPI": nome, "CA": ca, "Saldo Atual": qtd, "Estoque Mínimo": est_min})

        if val_ca_raw:
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
                try:
                    dt_val = datetime.strptime(str(val_ca_raw)[:10], fmt).date()
                    dias = (dt_val - hoje).days
                    if dias < 0:
                        cas_vencidos.append({"EPI": nome, "CA": ca, "Validade": formatar_data_br(dt_val), "Dias Vencido": abs(dias)})
                    elif dias <= 30:
                        cas_a_vencer.append({"EPI": nome, "CA": ca, "Validade": formatar_data_br(dt_val), "Dias Restantes": dias})
                    break
                except ValueError:
                    continue

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Saldo Geral", f"{saldo_total_unidades} un", f"{total_cadastrados} modelos")
    c2.metric("👥 Colaboradores Ativos", f"{total_colab_ativos}")
    c3.metric("🦺 Itens em Uso", f"{total_epis_em_uso} un")
    c4.metric("⛔ C.A. Vencidos", f"{len(cas_vencidos)}", delta=f"-{len(cas_vencidos)}" if cas_vencidos else None, delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.markdown("### ⚠️ Ponto de Reposição de Estoque")
        if itens_alerta_estoque:
            st.dataframe(itens_alerta_estoque, use_container_width=True, hide_index=True)
        else:
            st.success("✅ O almoxarifado opera em níveis seguros de estoque.")

    with col_dir:
        st.markdown("### 📅 Validade de C.A. (NR-6)")
        if cas_vencidos:
            st.error(f"⛔ **{len(cas_vencidos)}** EPI(s) com C.A. Vencido (Uso Bloqueado):")
            st.dataframe(cas_vencidos, use_container_width=True, hide_index=True)
        if cas_a_vencer:
            st.warning(f"🟡 **{len(cas_a_vencer)}** EPI(s) vencendo nos próximos 30 dias:")
            st.dataframe(cas_a_vencer, use_container_width=True, hide_index=True)
        if not cas_vencidos and not cas_a_vencer:
            st.success("✅ 100% dos EPIs cadastrados possuem C.A. válido.")

# ==========================================
# 1. CADASTRAR FUNCIONÁRIO
# ==========================================
elif menu == "Cadastrar Funcionário":
    st.title("👤 Gestão de Colaboradores")

    tab_cad, tab_cons = st.tabs(["➕ Cadastrar Novo Colaborador", "👥 Consultar & Editar Colaboradores"])

    with tab_cad:
        with st.form("form_funcionario_novo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo *", key="cad_func_nome")
                cpf = st.text_input("CPF (apenas números) *", max_chars=11, key="cad_func_cpf")
                matricula = st.text_input("Matrícula *", key="cad_func_mat")
            with col2:
                cargo = st.text_input("Cargo / Função *", key="cad_func_cargo")
                setor = st.text_input("Setor *", key="cad_func_setor")
                data_adm = st.date_input("Data de Admissão", format="DD/MM/YYYY", key="cad_func_adm")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Salvar Colaborador", use_container_width=True)

            if submitted:
                if nome and cpf and matricula and cargo and setor:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO funcionarios (nome, cpf, matricula, cargo, setor, data_admissao, status)
                            VALUES (?, ?, ?, ?, ?, ?, 'Ativo')
                        """, (nome.strip(), cpf.strip(), matricula.strip(), cargo.strip(), setor.strip(), data_adm))
                        conn.commit()
                        conn.close()
                        st.success(f"Colaborador {nome} cadastrado com sucesso!")
                    except sqlite3.IntegrityError:
                        st.error("Erro: CPF ou Matrícula já constam cadastrados.")
                else:
                    st.warning("Preencha todos os campos obrigatórios (*).")

    with tab_cons:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, cpf, matricula, cargo, setor, data_admissao, COALESCE(status, 'Ativo')
            FROM funcionarios
            ORDER BY nome ASC
        """)
        todos_funcs = cursor.fetchall()
        conn.close()

        if todos_funcs:
            lista_funcs = []
            for f in todos_funcs:
                lista_funcs.append({
                    "ID": f[0],
                    "Nome": f[1],
                    "CPF": f[2],
                    "Matrícula": f[3],
                    "Cargo": f[4],
                    "Setor": f[5],
                    "Admissão": formatar_data_br(f[6]),
                    "Status": f[7]
                })

            col_pesq, col_status = st.columns([3, 1])
            with col_pesq:
                termo_f = st.text_input("🔎 Pesquisar Colaborador:", placeholder="Digite nome, CPF, matrícula...", key="pesquisa_dinamica_func").strip().lower()
            with col_status:
                filtro_status = st.selectbox("Status:", ["Todos", "Ativo", "Inativo"], key="filtro_status_func")

            funcs_filtrados = lista_funcs
            if termo_f:
                funcs_filtrados = [f for f in funcs_filtrados if termo_f in f["Nome"].lower() or termo_f in f["CPF"].lower() or termo_f in f["Matrícula"].lower() or termo_f in f["Cargo"].lower()]

            if filtro_status != "Todos":
                funcs_filtrados = [f for f in funcs_filtrados if f["Status"] == filtro_status]

            itens_pag = 10
            total_pags_func = max(1, (len(funcs_filtrados) + itens_pag - 1) // itens_pag)
            if "pag_func_atual" not in st.session_state: st.session_state.pag_func_atual = 1
            if st.session_state.pag_func_atual > total_pags_func: st.session_state.pag_func_atual = total_pags_func

            inicio_f = (st.session_state.pag_func_atual - 1) * itens_pag
            pagina_funcs = funcs_filtrados[inicio_f:inicio_f + itens_pag]

            tabela_exibir_func = [
                {
                    "Nome": f["Nome"],
                    "CPF": f["CPF"],
                    "Matrícula": f["Matrícula"],
                    "Cargo / Função": f["Cargo"],
                    "Setor": f["Setor"],
                    "Data Admissão": f["Admissão"],
                    "Status": "🟢 Ativo" if f["Status"] == "Ativo" else "🔴 Inativo"
                }
                for f in pagina_funcs
            ]

            st.caption(f"Mostrando **{len(pagina_funcs)}** colaboradores (Página {st.session_state.pag_func_atual} de {total_pags_func}). Clique na linha para editar:")
            evento_tab_func = st.dataframe(tabela_exibir_func, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun", key="tabela_funcs_interativa")

            if total_pags_func > 1:
                cp1, cp2, cp3 = st.columns([1, 2, 1])
                with cp1:
                    if st.button("⬅️ Anterior", disabled=(st.session_state.pag_func_atual == 1), key="btn_ant_func"):
                        st.session_state.pag_func_atual -= 1
                        st.rerun()
                with cp2:
                    st.markdown(f"<p style='text-align: center; color: #1F2E3A;'><b>Página {st.session_state.pag_func_atual} de {total_pags_func}</b></p>", unsafe_allow_html=True)
                with cp3:
                    if st.button("Próxima ➡️", disabled=(st.session_state.pag_func_atual == total_pags_func), key="btn_prox_func"):
                        st.session_state.pag_func_atual += 1
                        st.rerun()

            linhas_sel = evento_tab_func.selection.rows if hasattr(evento_tab_func, "selection") else []
            if len(linhas_sel) > 0 and list(linhas_sel)[0] < len(pagina_funcs):
                id_escolhido = pagina_funcs[list(linhas_sel)[0]]["ID"]
                func_sel = next((f for f in todos_funcs if f[0] == id_escolhido), None)

                if func_sel:
                    st.markdown("---")
                    st.subheader(f"✏️ Editar: {func_sel[1]} (Matrícula: {func_sel[3]})")
                    
                    f_adm_date = datetime.now().date()
                    if func_sel[6]:
                        for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
                            try:
                                f_adm_date = datetime.strptime(str(func_sel[6])[:10], fmt).date()
                                break
                            except ValueError: pass

                    with st.form(f"form_ed_func_{func_sel[0]}", clear_on_submit=False):
                        c1, c2 = st.columns(2)
                        with c1:
                            ed_nome = st.text_input("Nome Completo *", value=func_sel[1], key=f"ef_nome_{func_sel[0]}")
                            ed_cpf = st.text_input("CPF *", value=func_sel[2], max_chars=11, key=f"ef_cpf_{func_sel[0]}")
                            ed_mat = st.text_input("Matrícula *", value=func_sel[3], key=f"ef_mat_{func_sel[0]}")
                        with c2:
                            ed_cargo = st.text_input("Cargo *", value=func_sel[4], key=f"ef_cargo_{func_sel[0]}")
                            ed_setor = st.text_input("Setor *", value=func_sel[5], key=f"ef_setor_{func_sel[0]}")
                            ed_adm = st.date_input("Data de Admissão", value=f_adm_date, format="DD/MM/YYYY", key=f"ef_adm_{func_sel[0]}")

                        ed_status = st.selectbox("Status:", ["Ativo", "Inativo"], index=0 if func_sel[7] == "Ativo" else 1, key=f"ef_st_{func_sel[0]}")

                        col_s, col_e = st.columns([3, 1])
                        with col_s:
                            btn_salvar = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                        with col_e:
                            chk_del = st.checkbox("Confirmar exclusão?", key=f"chk_fdel_{func_sel[0]}")
                            btn_del = st.form_submit_button("🗑️ Excluir Colaborador", use_container_width=True)

                        if btn_salvar:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE funcionarios SET nome=?, cpf=?, matricula=?, cargo=?, setor=?, data_admissao=?, status=? WHERE id=?",
                                           (ed_nome.strip(), ed_cpf.strip(), ed_mat.strip(), ed_cargo.strip(), ed_setor.strip(), ed_adm, ed_status, func_sel[0]))
                            conn.commit()
                            conn.close()
                            st.success("Dados atualizados com sucesso!")
                            st.rerun()

                        if btn_del:
                            if chk_del:
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute("SELECT COUNT(*) FROM entregas WHERE funcionario_id = ?", (func_sel[0],))
                                if cursor.fetchone()[0] > 0:
                                    st.error("⛔ Não é possível excluir colaborador com histórico de entregas. Altere o status para Inativo.")
                                    conn.close()
                                else:
                                    cursor.execute("DELETE FROM funcionarios WHERE id = ?", (func_sel[0],))
                                    conn.commit()
                                    conn.close()
                                    st.success("Colaborador excluído!")
                                    st.rerun()
                            else:
                                st.warning("Confirme a caixa de exclusão para autorizar.")
        else:
            st.info("Nenhum funcionário cadastrado ainda.")

# ==========================================
# 2. CONTROLE DE ESTOQUE DE EPI
# ==========================================
elif menu == "Estoque de EPIs":
    st.title("📦 Gestão de Estoque de EPIs")
    
    tab1, tab2 = st.tabs(["➕ Cadastrar Novo EPI (Busca CA)", "🔍 Consultar & Editar Estoque"])
    
    with tab1:
        st.markdown("### 🔍 Busca Técnica Automatizada")
        col_ca_busca, col_btn_busca = st.columns([3, 1])
        
        with col_ca_busca:
            ca_input_busca = st.text_input("Digite o número do C.A. para consulta oficial:", key="ca_busca_tab1")
        with col_btn_busca:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            buscar_ca = st.button("Buscar Ficha Técnica", use_container_width=True, key="btn_busca_tab1")

        if "dados_ca_detalhado" not in st.session_state:
            st.session_state.dados_ca_detalhado = None

        if buscar_ca and ca_input_busca:
            with st.spinner("Puxando laudos, normas e fabricante do Consulta CA..."):
                resultado = consultar_dados_ca(ca_input_busca)
                if resultado.get("sucesso"):
                    st.session_state.dados_ca_detalhado = resultado
                    st.success(f"✅ Ficha técnica do CA nº {ca_input_busca} carregada!")
                else:
                    st.error(resultado.get("mensagem", "Erro ao consultar CA."))
                    st.session_state.dados_ca_detalhado = None

        dados_det = st.session_state.dados_ca_detalhado or {}
        ca_esta_vencido = False
        val_data_default = datetime.now().date()
        hoje = datetime.now().date()

        if dados_det.get("validade_iso"):
            try:
                val_data_default = datetime.strptime(dados_det["validade_iso"], "%Y-%m-%d").date()
                if val_data_default < hoje:
                    ca_esta_vencido = True
            except Exception: pass

        if dados_det.get("situacao") == "VENCIDO":
            ca_esta_vencido = True

        st.markdown("---")
        if ca_esta_vencido:
            data_val_alerta = formatar_data_br(dados_det.get("validade", val_data_default.strftime('%Y-%m-%d')))
            st.error(f"⛔ **ATENÇÃO (NR-6):** O C.A. nº **{dados_det.get('ca', '')}** está **VENCIDO** desde **{data_val_alerta}**. Fornecimento proibido!")
        elif dados_det.get("ca"):
            data_val_alerta = formatar_data_br(dados_det.get("validade", val_data_default.strftime('%Y-%m-%d')))
            st.info(f"✅ C.A. nº **{dados_det.get('ca')}** regular até **{data_val_alerta}**.")

        with st.form("form_epi_completo", clear_on_submit=False):
            st.markdown("#### 🦺 Identificação e Saldo")
            col1, col2 = st.columns(2)
            with col1:
                ca_final = st.text_input("Número do CA *", value=dados_det.get("ca", ""), key="cad_ca")
                nome_epi = st.text_input("Nome do Equipamento *", value=dados_det.get("equipamento", ""), key="cad_nome")
                fabricante = st.text_input("Fabricante *", value=dados_det.get("razao_social", ""), key="cad_fab")
                situacao_texto = "🔴 VENCIDO (NÃO UTILIZAR)" if ca_esta_vencido else dados_det.get("situacao", "VÁLIDO")
                situacao_ca = st.text_input("Situação do CA", value=situacao_texto, key="cad_sit")
            with col2:
                validade_ca = st.date_input("Validade do CA", value=val_data_default, format="DD/MM/YYYY", key="cad_val")
                qtd_inicial = st.number_input("Quantidade Inicial *", min_value=0, step=1, value=10, key="cad_qtd")
                est_minimo = st.number_input("Estoque Mínimo (Alerta) *", min_value=1, value=5, key="cad_min")
                natureza_ca = st.text_input("Natureza", value=dados_det.get("natureza", "Nacional"), key="cad_nat")

            st.markdown("#### 📝 Descrição do Equipamento")
            desc_completa = st.text_area("Descrição Completa", value=dados_det.get("descricao_completa", ""), height=80, key="cad_desc")

            st.markdown("#### 🏭 Dados do Fabricante")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                cnpj_fab = st.text_input("CNPJ", value=dados_det.get("cnpj", ""), key="cad_cnpj")
                fantasia_fab = st.text_input("Nome Fantasia", value=dados_det.get("nome_fantasia", ""), key="cad_fantasia")
                site_fab = st.text_input("Site", value=dados_det.get("site", ""), key="cad_site")
            with col_f2:
                cidade_uf = st.text_input("Cidade/UF", value=dados_det.get("cidade_uf", ""), key="cad_cid")
                avaliacao = st.text_input("Avaliação Geral", value=dados_det.get("avaliacao_geral", ""), key="cad_aval")
                total_cas = st.text_input("Total de CAs", value=dados_det.get("total_cas_fabricante", ""), key="cad_totcas")

            st.markdown("#### 🔍 Dados Complementares & Aplicação")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                num_processo = st.text_input("N° Processo", value=dados_det.get("processo", ""), key="cad_proc")
                marcacao = st.text_input("Marcação", value=dados_det.get("marcacao", ""), key="cad_marc")
                referencias = st.text_input("Referências", value=dados_det.get("referencias", ""), key="cad_ref")
            with col_c2:
                aprovado_para = st.text_area("Aprovado Para", value=dados_det.get("aprovado_para", ""), height=100, key="cad_aprov")

            st.markdown("#### 🔬 Laudos & Normas")
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                num_laudo = st.text_input("N° do Laudo", value=dados_det.get("num_laudo", ""), key="cad_laudo")
                cnpj_lab = st.text_input("CNPJ Laboratório", value=dados_det.get("cnpj_laboratorio", ""), key="cad_cnpjlab")
                razao_lab = st.text_input("Razão Social Lab", value=dados_det.get("razao_laboratorio", ""), key="cad_razaolab")
            with col_l2:
                normas_txt = "\n".join(dados_det.get("normas", [])) if dados_det.get("normas") else ""
                normas_editavel = st.text_area("Normas Regulamentadoras", value=normas_txt, height=125, key="cad_normas")

            st.markdown("<br>", unsafe_allow_html=True)
            label_botao = "⚠️ Salvar EPI Vencido (Bloqueado p/ Entrega)" if ca_esta_vencido else "Salvar no Estoque"
            btn_salvar_epi = st.form_submit_button(label_botao, use_container_width=True)

            if btn_salvar_epi:
                if nome_epi and ca_final:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO epis (
                            nome, ca, fabricante, validade_ca, quantidade, estoque_minimo,
                            processo, natureza, descricao_completa, cnpj_fabricante,
                            nome_fantasia, site_fabricante, cidade_uf, avaliacao_geral,
                            total_cas_fabricante, marcacao, referencias, aprovado_para,
                            num_laudo, cnpj_laboratorio, razao_laboratorio, normas
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        nome_epi.strip(), ca_final.strip(), fabricante.strip(), validade_ca, qtd_inicial, est_minimo,
                        num_processo.strip(), natureza_ca.strip(), desc_completa.strip(), cnpj_fab.strip(),
                        fantasia_fab.strip(), site_fab.strip(), cidade_uf.strip(), avaliacao.strip(),
                        total_cas.strip(), marcacao.strip(), referencias.strip(), aprovado_para.strip(),
                        num_laudo.strip(), cnpj_lab.strip(), razao_lab.strip(), normas_editavel.strip()
                    ))
                    conn.commit()
                    conn.close()
                    st.success(f"EPI '{nome_epi}' cadastrado com sucesso!")
                    st.session_state.dados_ca_detalhado = None
                    st.rerun()
                else:
                    st.warning("Preencha ao menos Nome e CA.")

    with tab2:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, ca, fabricante, validade_ca, quantidade, estoque_minimo,
                   processo, natureza, descricao_completa, cnpj_fabricante,
                   nome_fantasia, site_fabricante, cidade_uf, avaliacao_geral,
                   total_cas_fabricante, marcacao, referencias, aprovado_para,
                   num_laudo, cnpj_laboratorio, razao_laboratorio, normas
            FROM epis ORDER BY nome ASC
        """)
        epis = cursor.fetchall()
        conn.close()

        if epis:
            hoje = datetime.now().date()
            lista_completa = []
            for epi in epis:
                val_ca_raw = epi[4]
                status_ca = "Sem data"
                dias_restantes = None
                ca_vencido_flag = False

                if val_ca_raw:
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
                        try:
                            val_ca_date = datetime.strptime(str(val_ca_raw).strip()[:10], fmt).date()
                            dias_restantes = (val_ca_date - hoje).days
                            if dias_restantes < 0:
                                status_ca = "🔴 CA Vencido"
                                ca_vencido_flag = True
                            elif dias_restantes <= 30:
                                status_ca = f"🟡 Vence em {dias_restantes}d"
                            else:
                                status_ca = "🟢 Válido"
                            break
                        except ValueError: pass

                status_estoque = "🟢 Regular" if epi[5] > epi[6] else "🔴 Repor"
                lista_completa.append({
                    "ID": epi[0],
                    "Equipamento": epi[1],
                    "CA": str(epi[2]),
                    "Fabricante": epi[3] or "",
                    "Validade CA": formatar_data_br(epi[4]),
                    "Status CA": status_ca,
                    "Saldo Atual": epi[5],
                    "Mínimo": epi[6],
                    "Status Estoque": status_estoque,
                    "vencido": ca_vencido_flag
                })

            col_busca, col_filtro_ca, col_filtro_est = st.columns([3, 2, 2])
            with col_busca:
                termo_busca = st.text_input("🔎 Pesquisar EPI / CA:", placeholder="Ex: luva, bot, 15306...", key="busca_dinamica_epi").strip().lower()
            with col_filtro_ca:
                filtro_ca = st.selectbox("Status CA:", ["Todos", "🟢 Válidos", "🟡 Vencendo em 30d", "🔴 Vencidos"])
            with col_filtro_est:
                filtro_estoque = st.selectbox("Estoque:", ["Todos", "🟢 Regular", "🔴 Repor"])

            itens_filtrados = lista_completa
            if termo_busca:
                itens_filtrados = [it for it in itens_filtrados if termo_busca in it["Equipamento"].lower() or termo_busca in it["CA"].lower()]
            if filtro_ca == "🟢 Válidos":
                itens_filtrados = [it for it in itens_filtrados if "🟢" in it["Status CA"]]
            elif filtro_ca == "🟡 Vencendo em 30d":
                itens_filtrados = [it for it in itens_filtrados if "🟡" in it["Status CA"]]
            elif filtro_ca == "🔴 Vencidos":
                itens_filtrados = [it for it in itens_filtrados if it["vencido"]]
            if filtro_estoque == "🟢 Regular":
                itens_filtrados = [it for it in itens_filtrados if it["Status Estoque"] == "🟢 Regular"]
            elif filtro_estoque == "🔴 Repor":
                itens_filtrados = [it for it in itens_filtrados if it["Status Estoque"] == "🔴 Repor"]

            itens_por_pagina = 10
            total_paginas = max(1, (len(itens_filtrados) + itens_por_pagina - 1) // itens_por_pagina)
            if "pagina_atual_estoque" not in st.session_state: st.session_state.pagina_atual_estoque = 1
            if st.session_state.pagina_atual_estoque > total_paginas: st.session_state.pagina_atual_estoque = total_paginas

            idx_inicio = (st.session_state.pagina_atual_estoque - 1) * itens_por_pagina
            pagina_itens = itens_filtrados[idx_inicio:idx_inicio + itens_por_pagina]

            tabela_exibicao = [
                {
                    "Equipamento": it["Equipamento"],
                    "CA": it["CA"],
                    "Fabricante": it["Fabricante"],
                    "Validade": it["Validade CA"],
                    "Status CA": it["Status CA"],
                    "Saldo": it["Saldo Atual"],
                    "Mín": it["Mínimo"],
                    "Situação": it["Status Estoque"]
                }
                for it in pagina_itens
            ]

            st.caption(f"Mostrando **{len(pagina_itens)}** de {len(itens_filtrados)} itens. Clique na linha para abrir a ficha completa:")
            evento_tabela = st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun", key="tabela_estoque_interativa")

            if total_paginas > 1:
                col_pag_ant, col_pag_info, col_pag_prox = st.columns([1, 2, 1])
                with col_pag_ant:
                    if st.button("⬅️ Anterior", disabled=(st.session_state.pagina_atual_estoque == 1), key="btn_ant_est"):
                        st.session_state.pagina_atual_estoque -= 1
                        st.rerun()
                with col_pag_info:
                    st.markdown(f"<p style='text-align: center; color: #1F2E3A;'><b>Página {st.session_state.pagina_atual_estoque} de {total_paginas}</b></p>", unsafe_allow_html=True)
                with col_pag_prox:
                    if st.button("Próxima ➡️", disabled=(st.session_state.pagina_atual_estoque == total_paginas), key="btn_prox_est"):
                        st.session_state.pagina_atual_estoque += 1
                        st.rerun()

            linhas_sel = evento_tabela.selection.rows if hasattr(evento_tabela, "selection") else []
            if len(linhas_sel) > 0 and list(linhas_sel)[0] < len(pagina_itens):
                id_sel = pagina_itens[list(linhas_sel)[0]]["ID"]
                epi_sel = next((e for e in epis if e[0] == id_sel), None)

                if epi_sel:
                    st.markdown("---")
                    st.subheader(f"📋 Ficha Técnica & Edição: {epi_sel[1]} (CA: {epi_sel[2]})")

                    val_ed_date = datetime.now().date()
                    if epi_sel[4]:
                        for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
                            try:
                                val_ed_date = datetime.strptime(str(epi_sel[4])[:10], fmt).date()
                                break
                            except ValueError: pass

                    with st.form(f"form_ed_epi_{epi_sel[0]}", clear_on_submit=False):
                        st.markdown("#### 🦺 Identificação e Saldo")
                        c1, c2 = st.columns(2)
                        with c1:
                            novo_ca = st.text_input("Número do CA *", value=str(epi_sel[2]), key=f"e_ca_{epi_sel[0]}")
                            novo_nome = st.text_input("Nome do Equipamento *", value=epi_sel[1], key=f"e_nome_{epi_sel[0]}")
                            novo_fab = st.text_input("Fabricante", value=epi_sel[3] or "", key=f"e_fab_{epi_sel[0]}")
                        with c2:
                            nova_val = st.date_input("Validade do CA", value=val_ed_date, format="DD/MM/YYYY", key=f"e_val_{epi_sel[0]}")
                            novo_saldo = st.number_input("Saldo em Estoque", min_value=0, step=1, value=epi_sel[5], key=f"e_qtd_{epi_sel[0]}")
                            novo_min = st.number_input("Estoque Mínimo", min_value=1, step=1, value=epi_sel[6], key=f"e_min_{epi_sel[0]}")

                        st.markdown("#### 📝 Descrição Completa")
                        nova_desc = st.text_area("Descrição", value=epi_sel[9] or "", height=80, key=f"e_desc_{epi_sel[0]}")

                        st.markdown("#### 🏭 Dados do Fabricante")
                        cf1, cf2 = st.columns(2)
                        with cf1:
                            novo_cnpj_fab = st.text_input("CNPJ", value=epi_sel[10] or "", key=f"e_cnpj_{epi_sel[0]}")
                            novo_fantasia = st.text_input("Nome Fantasia", value=epi_sel[11] or "", key=f"e_fant_{epi_sel[0]}")
                        with cf2:
                            novo_site = st.text_input("Site", value=epi_sel[12] or "", key=f"e_site_{epi_sel[0]}")
                            nova_cidade = st.text_input("Cidade/UF", value=epi_sel[13] or "", key=f"e_cid_{epi_sel[0]}")

                        st.markdown("#### 🔬 Laudos & Normas")
                        cl1, cl2 = st.columns(2)
                        with cl1:
                            novo_laudo = st.text_input("N° do Laudo", value=epi_sel[19] or "", key=f"e_laudo_{epi_sel[0]}")
                            novo_cnpj_lab = st.text_input("CNPJ Laboratório", value=epi_sel[20] or "", key=f"e_cnpjlab_{epi_sel[0]}")
                        with cl2:
                            novas_normas = st.text_area("Normas Atendidas", value=epi_sel[22] or "", height=100, key=f"e_norm_{epi_sel[0]}")

                        col_s, col_e = st.columns([3, 1])
                        with col_s:
                            btn_att = st.form_submit_button("💾 Salvar Todas as Alterações", use_container_width=True)
                        with col_e:
                            chk_e_del = st.checkbox("Confirmar exclusão?", key=f"chk_ed_{epi_sel[0]}")
                            btn_e_del = st.form_submit_button("🗑️ Excluir EPI", use_container_width=True)

                        if btn_att:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE epis SET nome=?, ca=?, fabricante=?, validade_ca=?, quantidade=?, estoque_minimo=?,
                                descricao_completa=?, cnpj_fabricante=?, nome_fantasia=?, site_fabricante=?, cidade_uf=?,
                                num_laudo=?, cnpj_laboratorio=?, normas=? WHERE id=?
                            """, (novo_nome.strip(), novo_ca.strip(), novo_fab.strip(), nova_val, novo_saldo, novo_min,
                                  nova_desc.strip(), novo_cnpj_fab.strip(), novo_fantasia.strip(), novo_site.strip(), nova_cidade.strip(),
                                  novo_laudo.strip(), novo_cnpj_lab.strip(), novas_normas.strip(), epi_sel[0]))
                            conn.commit()
                            conn.close()
                            st.success("EPI atualizado com sucesso!")
                            st.rerun()

                        if btn_e_del:
                            if chk_e_del:
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute("SELECT COUNT(*) FROM entregas WHERE epi_id = ?", (epi_sel[0],))
                                if cursor.fetchone()[0] > 0:
                                    st.error("⛔ Não é possível excluir EPI com histórico de entregas.")
                                    conn.close()
                                else:
                                    cursor.execute("DELETE FROM matriz_epi_cargo WHERE epi_id = ?", (epi_sel[0],))
                                    cursor.execute("DELETE FROM epis WHERE id = ?", (epi_sel[0],))
                                    conn.commit()
                                    conn.close()
                                    st.success("EPI removido com sucesso!")
                                    st.rerun()
                            else:
                                st.warning("Marque a confirmação para excluir.")
        else:
            st.info("Nenhum EPI cadastrado ainda.")

# ==========================================
# 3. REGISTRAR ENTREGA DE EPI
# ==========================================
elif menu == "Registrar Entrega de EPI":
    st.title("✍️ Registro de Entrega e Cautela de EPI")
    st.caption("Preencha a cautela de fornecimento e colha a assinatura digital do colaborador.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, matricula, cargo FROM funcionarios WHERE status='Ativo' ORDER BY nome ASC")
    funcs = cursor.fetchall()

    if not funcs:
        st.warning("Cadastre funcionários primeiro antes de registrar entregas.")
        conn.close()
    else:
        func_dict = {f"{f[1]} (Matrícula: {f[2]} | Cargo: {f[3]})": (f[0], f[3]) for f in funcs}
        colab_escolhido = st.selectbox("Selecione o Colaborador:", list(func_dict.keys()))
        func_id, cargo_colab = func_dict[colab_escolhido]

        cursor.execute("SELECT epi_id FROM matriz_epi_cargo WHERE cargo = ?", (cargo_colab,))
        epis_matriz_ids = [row[0] for row in cursor.fetchall()]

        col_filtro, _ = st.columns([2, 2])
        with col_filtro:
            filtrar_matriz = st.checkbox(f"🎯 Filtrar apenas EPIs da Matriz do cargo ({cargo_colab})", value=bool(epis_matriz_ids))

        if filtrar_matriz and epis_matriz_ids:
            placeholders = ",".join("?" for _ in epis_matriz_ids)
            cursor.execute(f"SELECT id, nome, ca, quantidade, validade_ca FROM epis WHERE id IN ({placeholders}) ORDER BY nome ASC", epis_matriz_ids)
        else:
            cursor.execute("SELECT id, nome, ca, quantidade, validade_ca FROM epis ORDER BY nome ASC")
        
        epis_disponiveis = cursor.fetchall()
        conn.close()

        if not epis_disponiveis:
            st.warning("Nenhum EPI disponível no estoque.")
        else:
            epi_dict = {f"{e[1]} - CA: {e[2]} (Saldo: {e[3]})": (e[0], e[3], e[4], e[2]) for e in epis_disponiveis}
            col1, col2 = st.columns(2)
            with col1:
                motivo = st.selectbox("Motivo da Entrega:", ["Admissional", "Substituição por Desgaste", "Extravio/Dano", "Mudança de Função"])
            with col2:
                epi_escolhido = st.selectbox("Selecione o EPI:", list(epi_dict.keys()))
                dados_epi_sel = epi_dict[epi_escolhido]
                qtd_max = dados_epi_sel[1]

                if qtd_max <= 0:
                    st.error("⚠️ Este EPI está com saldo ZERO no estoque.")
                    qtd_entregar = 0
                    saldo_zerado = True
                else:
                    qtd_entregar = st.number_input("Quantidade a Entregar:", min_value=1, max_value=qtd_max, value=1)
                    saldo_zerado = False

            val_ca_raw = dados_epi_sel[2]
            ca_bloqueado = False
            val_ca_date = None

            if val_ca_raw:
                for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
                    try:
                        val_ca_date = datetime.strptime(str(val_ca_raw).strip()[:10], fmt).date()
                        break
                    except ValueError: pass

            if val_ca_date:
                hoje = datetime.now().date()
                dias_restantes = (val_ca_date - hoje).days
                data_val_formatada = formatar_data_br(val_ca_date)
                if dias_restantes < 0:
                    st.error(f"⛔ **BLOQUEIO NR-6:** O CA nº **{dados_epi_sel[3]}** venceu em **{data_val_formatada}**. Entrega proibida!")
                    ca_bloqueado = True
                elif dias_restantes <= 30:
                    st.warning(f"⚠️ **ATENÇÃO:** O CA nº **{dados_epi_sel[3]}** vence em {dias_restantes} dias ({data_val_formatada}).")
                else:
                    st.success(f"✅ CA nº **{dados_epi_sel[3]}** válido até **{data_val_formatada}**.")

            travar_botao = ca_bloqueado or saldo_zerado

            st.markdown("---")
            st.subheader("Termo de Recebimento & Assinatura Digital")
            st.caption("Declaro ter recebido os EPIs descritos em perfeito estado, comprometendo-me ao uso obrigatório conforme NR-6.")

            # Inicializa estados de controle da assinatura
            if "canvas_expandido" not in st.session_state:
                st.session_state.canvas_expandido = False
            if "assinatura_salva_img" not in st.session_state:
                st.session_state.assinatura_salva_img = None

            col_exp, col_limp = st.columns([3, 1])
            with col_exp:
                lbl_exp = "🔍 Recolher Área de Assinatura" if st.session_state.canvas_expandido else "📱 Expandir Área de Assinatura (Modo Celular)"
                if st.button(lbl_exp, key="btn_toggle_expandir"):
                    st.session_state.canvas_expandido = not st.session_state.canvas_expandido
                    st.rerun()

            if st.session_state.canvas_expandido:
                largura_canvas = 700
                altura_canvas = 320
            else:
                largura_canvas = 480
                altura_canvas = 160

            st.markdown(
                """
                <div style="border: 2px dashed #D8C7A8; border-radius: 10px; padding: 6px; display: inline-block; background-color: #FFFFFF;">
                """, 
                unsafe_allow_html=True
            )

            bg_imagem = None
            if st.session_state.assinatura_salva_img is not None:
                bg_imagem = st.session_state.assinatura_salva_img.resize((largura_canvas, altura_canvas))

            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=3,
                stroke_color="#000000",
                background_color="#FFFFFF",
                background_image=bg_imagem,
                height=altura_canvas,
                width=largura_canvas,
                drawing_mode="freedraw",
                return_image_data=True,
                key=f"canvas_assinatura_entrega_{st.session_state.canvas_expandido}",
            )

            st.markdown("</div>", unsafe_allow_html=True)
            st.caption("✍️ Assine com o dedo ou caneta touch no espaço branco acima.")

            if canvas_result.image_data is not None and canvas_result.image_data[:, :, 3].sum() > 0:
                st.session_state.assinatura_salva_img = Image.fromarray(canvas_result.image_data.astype("uint8"))

            with col_limp:
                if st.button("🗑️ Limpar Assinatura", key="btn_limpar_canvas"):
                    st.session_state.assinatura_salva_img = None
                    st.rerun()

            if st.button("Confirmar Entrega e Dar Baixa", disabled=travar_botao, use_container_width=True):
                tem_desenho_ativo = canvas_result.image_data is not None and canvas_result.image_data[:, :, 3].sum() > 0
                tem_desenho_sessao = st.session_state.assinatura_salva_img is not None

                if tem_desenho_ativo or tem_desenho_sessao:
                    epi_id = dados_epi_sel[0]
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    caminho_ass = os.path.join("assinaturas", f"ass_{func_id}_{timestamp_str}.png")

                    if tem_desenho_ativo:
                        imagem_final = Image.fromarray(canvas_result.image_data.astype("uint8"))
                    else:
                        imagem_final = st.session_state.assinatura_salva_img

                    imagem_final.save(caminho_ass)

                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO entregas (funcionario_id, epi_id, quantidade, motivo, caminho_assinatura, status_item)
                        VALUES (?, ?, ?, ?, ?, 'Em Uso')
                    """, (func_id, epi_id, qtd_entregar, motivo, caminho_ass))
                    cursor.execute("UPDATE epis SET quantidade = quantidade - ? WHERE id = ?", (qtd_entregar, epi_id))
                    conn.commit()
                    conn.close()

                    st.session_state.assinatura_salva_img = None
                    st.session_state.canvas_expandido = False

                    st.success("Entrega registrada e saldo de estoque atualizado!")
                    st.rerun()
                else:
                    st.error("Colete a assinatura do colaborador no quadro antes de confirmar.")

# ==========================================
# 4. DEVOLUÇÃO DE EPI
# ==========================================
elif menu == "Devolução de EPI":
    st.title("🔄 Registro de Devolução / Troca")
    st.caption("Dê baixa nos itens em posse dos colaboradores e retorne ao estoque se aplicável.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, matricula FROM funcionarios WHERE status='Ativo' ORDER BY nome ASC")
    funcs = cursor.fetchall()

    if funcs:
        func_map = {f"{f[1]} (Matrícula: {f[2]})": f[0] for f in funcs}
        colab_sel = st.selectbox("Selecione o Colaborador:", list(func_map.keys()))
        func_id = func_map[colab_sel]

        cursor.execute("""
            SELECT e.id, p.nome, p.ca, e.quantidade, e.data_entrega, e.epi_id
            FROM entregas e
            JOIN epis p ON e.epi_id = p.id
            WHERE e.funcionario_id = ? AND COALESCE(e.status_item, 'Em Uso') = 'Em Uso'
            ORDER BY e.data_entrega DESC
        """, (func_id,))
        itens_pendentes = cursor.fetchall()

        if itens_pendentes:
            opcoes_itens = {f"#{item[0]} - {item[1]} (CA: {item[2]}) | Qtd: {item[3]} | Entregue em: {formatar_data_br(item[4])}": item for item in itens_pendentes}
            item_escolhido = st.selectbox("Selecione o item para devolver:", list(opcoes_itens.keys()))
            dados_item = opcoes_itens[item_escolhido]

            col1, col2 = st.columns(2)
            with col1:
                motivo_dev = st.selectbox("Motivo da Devolução:", ["Desgaste Natural (Descarte)", "Danificado / Quebrado", "Devolução ao Estoque (Reutilizável)", "Desligamento"])
            with col2:
                retornar_ao_estoque = st.checkbox("Retornar unidades para o saldo do estoque?")

            if st.button("Confirmar Devolução", use_container_width=True):
                entrega_id, epi_id, qtd_dev = dados_item[0], dados_item[5], dados_item[3]
                data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute("UPDATE entregas SET data_devolucao=?, motivo_devolucao=?, status_item='Devolvido' WHERE id=?", (data_agora, motivo_dev, entrega_id))
                if retornar_ao_estoque:
                    cursor.execute("UPDATE epis SET quantidade = quantidade + ? WHERE id = ?", (qtd_dev, epi_id))
                conn.commit()
                conn.close()
                st.success("Devolução concluída com sucesso!")
                st.rerun()
        else:
            conn.close()
            st.info("Este colaborador não possui nenhum EPI pendente de devolução.")
    else:
        conn.close()
        st.info("Nenhum funcionário cadastrado.")

# ==========================================
# 5. MATRIZ DE EPI POR CARGO
# ==========================================
elif menu == "Matriz de EPI por Cargo":
    st.title("🎯 Matriz de EPIs Obrigatórios por Função")
    st.caption("Defina quais equipamentos cada cargo deve receber obrigatoriamente.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT cargo FROM funcionarios ORDER BY cargo ASC")
    cargos = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id, nome, ca FROM epis ORDER BY nome ASC")
    todos_epis = cursor.fetchall()

    if not cargos or not todos_epis:
        st.warning("Cadastre funcionários e EPIs antes de configurar a matriz.")
        conn.close()
    else:
        cargo_sel = st.selectbox("Selecione o Cargo:", cargos)
        cursor.execute("SELECT m.id, p.nome, p.ca FROM matriz_epi_cargo m JOIN epis p ON m.epi_id = p.id WHERE m.cargo = ?", (cargo_sel,))
        epis_vinculados = cursor.fetchall()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### ➕ Vincular EPI ao Cargo: `{cargo_sel}`")
            epi_opcoes = {f"{e[1]} (CA: {e[2]})": e[0] for e in todos_epis}
            novo_epi_sel = st.selectbox("Selecione o EPI:", list(epi_opcoes.keys()))
            if st.button("Vincular ao Cargo", use_container_width=True):
                try:
                    cursor.execute("INSERT INTO matriz_epi_cargo (cargo, epi_id) VALUES (?, ?)", (cargo_sel, epi_opcoes[novo_epi_sel]))
                    conn.commit()
                    st.success("EPI vinculado com sucesso!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.warning("Este EPI já está vinculado a esse cargo.")

        with col2:
            st.markdown(f"#### 📋 EPIs Obrigatórios do Cargo ({len(epis_vinculados)})")
            if epis_vinculados:
                for vinc in epis_vinculados:
                    c_txt, c_btn = st.columns([3, 1])
                    c_txt.write(f"• **{vinc[1]}** (CA: {vinc[2]})")
                    if c_btn.button("Remover", key=f"del_mat_{vinc[0]}"):
                        cursor.execute("DELETE FROM matriz_epi_cargo WHERE id = ?", (vinc[0],))
                        conn.commit()
                        st.rerun()
            else:
                st.info("Nenhum EPI associado a este cargo ainda.")

        conn.close()

# ==========================================
# 6. HISTÓRICO / FICHA DE EPI
# ==========================================
elif menu == "Histórico / Ficha de EPI":
    st.title("📋 Ficha de EPI & Cautelas Individuais")
    st.caption("Visualize o prontuário de fornecimento e emita o PDF oficial assinado.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, matricula, cargo, setor, data_admissao FROM funcionarios ORDER BY nome ASC")
    funcs = cursor.fetchall()

    if funcs:
        func_map = {f"{f[1]} | Matrícula: {f[3]}": f for f in funcs}
        escolha = st.selectbox("Selecione o Colaborador:", list(func_map.keys()))
        colab = func_map[escolha]
        
        st.markdown(f"""
        <div style='background-color: #FFFFFF; border: 2px solid #D8C7A8; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 3px 6px rgba(31, 46, 58, 0.06);'>
            <b style='color: #1F2E3A;'>Colaborador:</b> <span style='color: #1F2E3A;'>{colab[1]}</span> &nbsp;|&nbsp; 
            <b style='color: #1F2E3A;'>Cargo:</b> <span style='color: #1F2E3A;'>{colab[4]}</span> &nbsp;|&nbsp; 
            <b style='color: #1F2E3A;'>Setor:</b> <span style='color: #1F2E3A;'>{colab[5]}</span><br>
            <b style='color: #1F2E3A;'>CPF:</b> <span style='color: #1F2E3A;'>{colab[2]}</span> &nbsp;|&nbsp; 
            <b style='color: #1F2E3A;'>Data Admissão:</b> <span style='color: #1F2E3A;'>{formatar_data_br(colab[6])}</span>
        </div>
        """, unsafe_allow_html=True)

        cursor.execute("""
            SELECT e.data_entrega, p.nome, p.ca, e.quantidade, e.motivo, e.caminho_assinatura,
                   e.data_devolucao, e.motivo_devolucao, COALESCE(e.status_item, 'Em Uso')
            FROM entregas e JOIN epis p ON e.epi_id = p.id
            WHERE e.funcionario_id = ? ORDER BY e.data_entrega ASC
        """, (colab[0],))
        registros = cursor.fetchall()
        conn.close()

        if registros:
            try:
                dados_pdf = gerar_ficha_pdf(colab, registros)
                st.download_button(
                    label="📄 Baixar Ficha Oficial em PDF (NR-6)",
                    data=dados_pdf,
                    file_name=f"Ficha_EPI_{colab[3]}_{colab[1].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

            st.markdown("<br>", unsafe_allow_html=True)
            for reg in reversed(registros):
                dt_entrega = formatar_data_br(reg[0])
                nome_epi, ca_num, qtd = reg[1], reg[2], reg[3]
                caminho_ass = reg[5]
                dt_dev = formatar_data_br(reg[6]) if reg[6] else None
                status_desc = f"Devolvido em {dt_dev} ({reg[7]})" if dt_dev else reg[8]

                c1, c2, c3, c4 = st.columns([2, 3, 2, 2])
                c1.write(f"**Data:** {dt_entrega}")
                c2.write(f"**EPI:** {nome_epi} (CA: {ca_num})")
                c3.write(f"**Qtd:** {qtd} un | **Status:** {status_desc}")
                with c4:
                    if caminho_ass and os.path.exists(caminho_ass):
                        st.image(caminho_ass, width=110, caption="Assinatura")
                    else:
                        st.caption("Sem assinatura")
                st.divider()
        else:
            st.info("Nenhuma entrega registrada para este funcionário.")
    else:
        conn.close()
        st.info("Nenhum funcionário cadastrado.")

# ==========================================
# 7. BACKUP & SEGURANÇA DOS DADOS
# ==========================================
elif menu == "Backup & Segurança":
    st.title("💾 Backup & Segurança de Dados")
    st.caption("Gere uma cópia de segurança completa do banco de dados e arquivos de assinatura.")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        > **Conformidade Legal:** Os registros de fornecimento de EPI devem ser guardados por no mínimo 20 anos para fins previdenciários e trabalhistas. Exporte backups regulares.
        """)
        total_ass = len([f for f in os.listdir("assinaturas") if f.endswith(".png")]) if os.path.exists("assinaturas") else 0
        st.write(f"• **Banco SQLite:** `gestao_epi.db` (Cadastros, histórico e estoque)")
        st.write(f"• **Assinaturas:** {total_ass} arquivo(s) salvos na pasta `assinaturas/`")

    with col2:
        buffer_zip = io.BytesIO()
        with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists("gestao_epi.db"):
                zf.write("gestao_epi.db", arcname="gestao_epi.db")
            if os.path.exists("assinaturas"):
                for raiz, _, arquivos in os.walk("assinaturas"):
                    for arq in arquivos:
                        zf.write(os.path.join(raiz, arq), arcname=os.path.relpath(os.path.join(raiz, arq), start="."))
        buffer_zip.seek(0)
        timestamp_backup = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="📦 Baixar Backup Completo (.ZIP)",
            data=buffer_zip.getvalue(),
            file_name=f"Backup_Gestao_EPI_{timestamp_backup}.zip",
            mime="application/zip",
            use_container_width=True
        )

# ==========================================
# RODAPÉ COM ASSINATURA
# ==========================================
st.markdown("""
<div class='footer-assinatura'>
    Sistema de Gestão de EPIs &copy; 2026 | Conformidade com a NR-6 e Portaria MTE<br>
    Criador: <b>Thiago Soares da Rocha</b>
</div>
""", unsafe_allow_html=True)