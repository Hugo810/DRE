import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
import json
import os

# -------------------------------
# Modelos
# -------------------------------
@dataclass
class ContaDRE:
    id: int
    nome: str
    dre_field: str
    tipo: str = "receita"  # 'receita', 'despesa', 'outro'

@dataclass
class Lancamento:
    id: int
    tipo: str                 # 'receber' ou 'pagar'
    data_vencimento: str      # 'DD/MM/YYYY'
    entidade: str             # cliente ou fornecedor
    descricao: str
    valor: float
    status: str               # 'Pendente', 'Recebido', 'Pago'
    data_baixa: str
    conta_banco: str
    conta_dre_id: Optional[int]
    categoria_texto: str = ""

# -------------------------------
# Sistema (lógica)
# -------------------------------
class Sistema:
    def __init__(self):
        self.contas_dre: List[ContaDRE] = []
        self.lancamentos: List[Lancamento] = []
        self.bancos: List[str] = []
        self.categorias: List[str] = []
        self.next_conta_dre_id = 1
        self.next_lanc_id = 1
        self.carregar_dados()
        
        # Se não carregou dados, carrega as contas padrão
        if not self.contas_dre:
            self.carregar_contas_dre_padrao()

    def carregar_contas_dre_padrao(self):
        padrao = [
            ("Venda de Mercadoria", "receita_bruta", "receita"),
            ("Impostos sobre Vendas", "impostos", "despesa"),
            ("Compra de Mercadoria", "custo", "despesa"),
            ("Despesas Administrativas", "despesas_administrativas", "despesa"),
            ("Distribuição de Lucro", "distribuicao_lucro", "despesa"),
            ("Investimento", "investimento", "outro"),
            ("Empréstimos", "emprestimos", "outro")
        ]
        for nome, field, tipo in padrao:
            self.adicionar_conta_dre(nome, field, tipo)

    # ------- Persistência de Dados -------
    def salvar_dados(self):
        """Salva todos os dados em arquivos JSON"""
        try:
            dados = {
                'contas_dre': [asdict(conta) for conta in self.contas_dre],
                'lancamentos': [asdict(lanc) for lanc in self.lancamentos],
                'bancos': self.bancos,
                'categorias': self.categorias,
                'next_conta_dre_id': self.next_conta_dre_id,
                'next_lanc_id': self.next_lanc_id
            }
            
            with open('dados_sistema.json', 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
                
            print("✅ Dados salvos com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")

    def carregar_dados(self):
        """Carrega os dados dos arquivos JSON"""
        try:
            if os.path.exists('dados_sistema.json'):
                with open('dados_sistema.json', 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                # Carregar contas DRE
                self.contas_dre = []
                for conta_data in dados.get('contas_dre', []):
                    conta = ContaDRE(**conta_data)
                    self.contas_dre.append(conta)
                
                # Carregar lançamentos
                self.lancamentos = []
                for lanc_data in dados.get('lancamentos', []):
                    # Garantir compatibilidade com versões anteriores
                    if 'categoria_texto' not in lanc_data:
                        lanc_data['categoria_texto'] = ""
                    lanc = Lancamento(**lanc_data)
                    self.lancamentos.append(lanc)
                
                # Carregar bancos e categorias
                self.bancos = dados.get('bancos', [])
                self.categorias = dados.get('categorias', [])
                
                # Carregar próximos IDs
                self.next_conta_dre_id = dados.get('next_conta_dre_id', 1)
                self.next_lanc_id = dados.get('next_lanc_id', 1)
                
                print("✅ Dados carregados com sucesso!")
                print(f"   - Contas DRE: {len(self.contas_dre)}")
                print(f"   - Lançamentos: {len(self.lancamentos)}")
                print(f"   - Bancos: {len(self.bancos)}")
                print(f"   - Categorias: {len(self.categorias)}")
                
            else:
                print("ℹ️  Nenhum arquivo de dados encontrado. Iniciando com dados padrão.")
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            # Em caso de erro, inicia com dados vazios
            self.contas_dre = []
            self.lancamentos = []
            self.bancos = []
            self.categorias = []
            self.next_conta_dre_id = 1
            self.next_lanc_id = 1

    # ------- Gerenciamento de Bancos -------
    def adicionar_banco(self, banco: str) -> bool:
        """Adiciona um novo banco à lista se não existir"""
        if banco and banco.strip() and banco not in self.bancos:
            self.bancos.append(banco.strip())
            self.bancos.sort()  # Mantém a lista ordenada
            self.salvar_dados()
            return True
        return False

    def remover_banco(self, banco: str) -> bool:
        """Remove um banco da lista"""
        if banco in self.bancos:
            self.bancos.remove(banco)
            self.salvar_dados()
            return True
        return False

    def obter_bancos(self) -> List[str]:
        """Retorna a lista de bancos"""
        return self.bancos

    # ------- Gerenciamento de Categorias -------
    def adicionar_categoria(self, categoria: str) -> bool:
        """Adiciona uma nova categoria à lista se não existir"""
        if categoria and categoria.strip() and categoria not in self.categorias:
            self.categorias.append(categoria.strip())
            self.categorias.sort()  # Mantém a lista ordenada
            self.salvar_dados()
            return True
        return False

    def remover_categoria(self, categoria: str) -> bool:
        """Remove uma categoria da lista"""
        if categoria in self.categorias:
            self.categorias.remove(categoria)
            self.salvar_dados()
            return True
        return False

    def obter_categorias(self) -> List[str]:
        """Retorna a lista de categorias"""
        return self.categorias

    # ------- Contas DRE -------
    def adicionar_conta_dre(self, nome: str, dre_field: str, tipo: str = "receita") -> ContaDRE:
        c = ContaDRE(self.next_conta_dre_id, nome, dre_field, tipo)
        self.contas_dre.append(c)
        self.next_conta_dre_id += 1
        self.salvar_dados()  # Salva automaticamente após adicionar
        return c

    def atualizar_conta_dre(self, conta_id: int, novo_nome: str, novo_dre_field: str, novo_tipo: str) -> bool:
        c = self.get_conta_dre(conta_id)
        if not c: return False
        c.nome = novo_nome
        c.dre_field = novo_dre_field
        c.tipo = novo_tipo
        self.salvar_dados()  # Salva automaticamente após atualizar
        return True

    def remover_conta_dre(self, conta_id: int) -> bool:
        for l in self.lancamentos:
            if l.conta_dre_id == conta_id:
                return False
        self.contas_dre = [c for c in self.contas_dre if c.id != conta_id]
        self.salvar_dados()  # Salva automaticamente após remover
        return True

    def get_conta_dre(self, conta_id: int) -> Optional[ContaDRE]:
        for c in self.contas_dre:
            if c.id == conta_id:
                return c
        return None

    def get_conta_dre_por_nome(self, nome: str) -> Optional[ContaDRE]:
        for c in self.contas_dre:
            if c.nome == nome:
                return c
        return None

    def get_contas_dre_por_tipo(self, tipo: str) -> List[ContaDRE]:
        """Retorna contas DRE filtradas por tipo"""
        return [c for c in self.contas_dre if c.tipo == tipo]

    # ------- Lançamentos -------
    def adicionar_lancamento(self, tipo, data_vencimento, entidade, descricao, valor, status, data_baixa, conta_banco, conta_dre_id, categoria_texto=""):
        # Validar data de baixa baseado no status
        if status == "Pendente" and data_baixa:
            messagebox.showwarning("Atenção", "Para status 'Pendente', a data de baixa não pode ser preenchida.")
            return None
            
        if status in ["Recebido", "Pago"] and not data_baixa:
            messagebox.showwarning("Atenção", f"Para status '{status}', a data de baixa é obrigatória.")
            return None
        
        # Converter valor para float
        if isinstance(valor, str):
            valor = float(valor.replace('.', '').replace(',', '.'))
        
        l = Lancamento(self.next_lanc_id, tipo, data_vencimento, entidade, descricao, valor, status, data_baixa or "", conta_banco or "", conta_dre_id, categoria_texto)
        self.lancamentos.append(l)
        self.next_lanc_id += 1
            
        print(f"✅ LANÇAMENTO ADICIONADO: ID {l.id}, Tipo: {tipo}, Status: {status}, Valor: R$ {valor}, Conta DRE ID: {conta_dre_id}")
        self.salvar_dados()  # Salva automaticamente após adicionar
        return l

    def atualizar_lancamento(self, lanc_id: int, **kwargs) -> bool:
        # Validar data de baixa baseado no status se estiver sendo atualizado
        if 'status' in kwargs and 'data_baixa' in kwargs:
            status = kwargs['status']
            data_baixa = kwargs['data_baixa']
            
            if status == "Pendente" and data_baixa:
                messagebox.showwarning("Atenção", "Para status 'Pendente', a data de baixa não pode ser preenchida.")
                return False
                
            if status in ["Recebido", "Pago"] and not data_baixa:
                messagebox.showwarning("Atenção", f"Para status '{status}', a data de baixa é obrigatória.")
                return False
        
        for l in self.lancamentos:
            if l.id == lanc_id:
                for k, v in kwargs.items():
                    if hasattr(l, k):
                        # Converter valor se necessário
                        if k == 'valor' and isinstance(v, str):
                            v = float(v.replace('.', '').replace(',', '.'))
                        setattr(l, k, v)
                    
                self.salvar_dados()  # Salva automaticamente após atualizar
                return True
        return False

    def remover_lancamento(self, lanc_id: int) -> bool:
        before = len(self.lancamentos)
        self.lancamentos = [l for l in self.lancamentos if l.id != lanc_id]
        if len(self.lancamentos) < before:
            self.salvar_dados()  # Salva automaticamente após remover
            return True
        return False

    # ------- Cálculo DRE -------
    def calcular_dre(self, data_inicio=None, data_fim=None):
        dre_vals = {
            'receita_bruta': 0.0,
            'impostos': 0.0,
            'receita_liquida': 0.0,
            'custo': 0.0,
            'lucro_bruto': 0.0,
            'despesas_administrativas': 0.0,
            'resultado_operacional': 0.0,
            'investimento': 0.0,
            'emprestimos': 0.0,
            'distribuicao_lucro': 0.0,
            'resultado_periodo': 0.0
        }
        
        # Se datas não foram fornecidas, usar datas padrão que incluem tudo
        usar_filtro_data = data_inicio and data_fim
        
        data_inicio_dt = None
        data_fim_dt = None
        
        if usar_filtro_data:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%d/%m/%Y')
                data_fim_dt = datetime.strptime(data_fim, '%d/%m/%Y')
                print(f"🔍 FILTRO ATIVADO: {data_inicio} a {data_fim}")
            except ValueError:
                print(f"❌ Datas inválidas - desativando filtro")
                usar_filtro_data = False
        else:
            print(f"🔓 SEM FILTRO DE DATA - incluindo todos os lançamentos")
        
        print(f"=== INICIANDO CÁLCULO DRE ===")
        print(f"Total de lançamentos: {len(self.lancamentos)}")
        
        # Primeiro, calcular todos os valores baseados nos lançamentos
        for l in self.lancamentos:
            print(f"📋 Analisando lançamento {l.id}: {l.tipo} - {l.descricao} - Status: {l.status} - Valor: R$ {l.valor}")

            # Verificar status primeiro
            if l.status not in ("Recebido", "Pago"):
                print(f"  ❌ Ignorado - status não é Recebido/Pago: {l.status}")
                continue
            
            # Verificar filtro de data pela data de baixa
            if usar_filtro_data:
                if not l.data_baixa:
                    print(f"  ❌ Ignorado - sem data de baixa (filtro ativo)")
                    continue
                    
                try:
                    data_baixa_dt = datetime.strptime(l.data_baixa, '%d/%m/%Y')
                    print(f"  📅 Data baixa: {l.data_baixa}")
                    
                    # Aplicar filtro de data
                    if data_baixa_dt < data_inicio_dt or data_baixa_dt > data_fim_dt:
                        print(f"  ⏰ Ignorado - fora do período do filtro")
                        continue
                        
                except ValueError:
                    print(f"  ❌ Data baixa inválida: {l.data_baixa}")
                    continue
            else:
                if l.data_baixa:
                    print(f"  📅 Data baixa: {l.data_baixa}")
                else:
                    print(f"  📅 Sem data de baixa (filtro inativo)")
                
            conta = self.get_conta_dre(l.conta_dre_id) if l.conta_dre_id else None
            if not conta:
                print(f"  ❌ Ignorado - conta DRE não encontrada (ID: {l.conta_dre_id})")
                continue
                
            campo = conta.dre_field
            print(f"  ✅ Processando: {conta.nome} ({campo}) - R$ {l.valor}")
            
            if campo in dre_vals:
                # Para receita bruta, custo, investimento, empréstimos e distribuição de lucro,
                # usamos o valor do lançamento normalmente
                dre_vals[campo] += l.valor
                print(f"  💰 {campo}: +{l.valor} = {dre_vals[campo]}")

        # Calcular valores derivados
        dre_vals['receita_liquida'] = dre_vals['receita_bruta'] - dre_vals['impostos']
        dre_vals['lucro_bruto'] = dre_vals['receita_liquida'] - dre_vals['custo']
        dre_vals['resultado_operacional'] = dre_vals['lucro_bruto'] - dre_vals['despesas_administrativas']
        dre_vals['resultado_periodo'] = dre_vals['resultado_operacional'] - dre_vals['distribuicao_lucro']
        
        print("=== RESULTADO DRE ===")
        for key, value in dre_vals.items():
            print(f"{key}: R$ {value}")
        print("=====================")
        
        return dre_vals

# -------------------------------
# Interface Gráfica
# -------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Contábil - DRE")
        self.geometry("1400x800")
        self.sistema = Sistema()

        # Configurar para salvar dados ao fechar a aplicação
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        # REMOVIDO: self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_contas_dre = ttk.Frame(self.notebook)
        self.tab_bancos = ttk.Frame(self.notebook)
        self.tab_categorias = ttk.Frame(self.notebook)
        self.tab_receber = ttk.Frame(self.notebook)
        self.tab_pagar = ttk.Frame(self.notebook)
        self.tab_dre = ttk.Frame(self.notebook)
        self.tab_fluxo_caixa = ttk.Frame(self.notebook)

        # REMOVIDO: self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.notebook.add(self.tab_contas_dre, text="Plano de Contas (DRE)")
        self.notebook.add(self.tab_bancos, text="Gerenciar Bancos")
        self.notebook.add(self.tab_categorias, text="Gerenciar Categorias")
        self.notebook.add(self.tab_receber, text="Contas a Receber")
        self.notebook.add(self.tab_pagar, text="Contas a Pagar")
        self.notebook.add(self.tab_dre, text="DRE")
        self.notebook.add(self.tab_fluxo_caixa, text="Fluxo de Caixa")

        # Chamadas para construir abas (REMOVIDA a do dashboard)
        # REMOVIDO: self._construir_dashboard()
        self._construir_contas_dre()
        self._construir_tab_bancos()
        self._construir_tab_categorias()
        self._construir_tab_lancamentos(self.tab_receber, "receber")
        self._construir_tab_lancamentos(self.tab_pagar, "pagar")
        self._construir_dre()
        self._construir_tab_fluxo_caixa()
        self.atualizar_todas_views()

    def ao_fechar(self):
        """Salva os dados antes de fechar a aplicação"""
        print("💾 Salvando dados antes de fechar...")
        self.sistema.salvar_dados()
        self.destroy()

    # ---------------- Helpers de máscara (tempo real) ----------------
    def _mascara_data_realtime(self, event, entry: ttk.Entry):
        texto = ''.join(ch for ch in entry.get() if ch.isdigit())[:8]
        novo = ""
        for i, ch in enumerate(texto):
            if i == 2 or i == 4:
                novo += '/' + ch
            else:
                novo += ch
        entry.delete(0, tk.END)
        entry.insert(0, novo)

    def _mascara_valor_realtime(self, event, entry: ttk.Entry):
        texto = ''.join(ch for ch in entry.get() if ch.isdigit())
        if texto == "":
            entry.delete(0, tk.END)
            entry.insert(0, "0,00")
            return
        if len(texto) <= 2:
            inteira = "0"
            centavos = texto.zfill(2)
        else:
            inteira = texto[:-2]
            centavos = texto[-2:]
        try:
            inteira_int = int(inteira)
            inteira_fmt = f"{inteira_int:,}".replace(",", ".")
        except:
            inteira_fmt = "0"
        valor_formatado = f"{inteira_fmt},{centavos}"
        entry.delete(0, tk.END)
        entry.insert(0, valor_formatado)

    def _get_data_atual(self):
        """Retorna a data atual no formato DD/MM/AAAA"""
        return datetime.now().strftime('%d/%m/%Y')

    def _get_primeiro_dia_mes_atual(self):
        """Retorna o primeiro dia do mês atual no formato DD/MM/AAAA"""
        hoje = datetime.now()
        primeiro_dia = hoje.replace(day=1)
        return primeiro_dia.strftime('%d/%m/%Y')

    def _get_ultimo_dia_mes_atual(self):
        """Retorna o último dia do mês atual no formato DD/MM/AAAA"""
        hoje = datetime.now()
        # Próximo mês
        if hoje.month == 12:
            proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
        else:
            proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
        # Último dia do mês atual é o dia anterior ao primeiro dia do próximo mês
        from datetime import timedelta
        ultimo_dia = proximo_mes - timedelta(days=1)
        return ultimo_dia.strftime('%d/%m/%Y')

    def _extrair_id_conta_dre(self, texto_combo: str) -> Optional[int]:
        """Extrai o ID da conta DRE a partir do texto do combobox"""
        if not texto_combo or " - " not in texto_combo:
            return None
        try:
            return int(texto_combo.split(" - ")[0])
        except ValueError:
            return None

    def _get_contas_dre_filtradas(self, tipo_lancamento: str) -> List[str]:
        """Retorna lista de contas DRE filtradas por tipo de lançamento"""
        if tipo_lancamento == "receber":
            # Para contas a receber: apenas contas do tipo receita e outro
            contas_filtradas = [c for c in self.sistema.contas_dre if c.tipo in ["receita", "outro"]]
        else:  # pagar
            # Para contas a pagar: apenas contas do tipo despesa e outro
            contas_filtradas = [c for c in self.sistema.contas_dre if c.tipo in ["despesa", "outro"]]
        
        return [f"{c.id} - {c.nome}" for c in contas_filtradas]

    def _bind_mascaras_em_entry(self, entry: ttk.Entry, tipo: str):
        if tipo == "data":
            entry.bind('<KeyRelease>', lambda e, ent=entry: self._mascara_data_realtime(e, ent))
        elif tipo == "valor":
            def on_keypress(e):
                if e.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab']:
                    return
                if not (e.char.isdigit() or e.char == ','):
                    return "break"
            entry.bind('<KeyPress>', on_keypress)
            entry.bind('<KeyRelease>', lambda e, ent=entry: self._mascara_valor_realtime(e, ent))

    # ---------------- Plano de Contas DRE (CRUD) ----------------
    def _construir_contas_dre(self):
        f = ttk.Frame(self.tab_contas_dre, padding=8)
        f.pack(fill="both", expand=True)

        # Formulário
        frm_top = ttk.Frame(f)
        frm_top.pack(fill="x", pady=6)

        ttk.Label(frm_top, text="Nome da Conta DRE:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.entry_dre_nome = ttk.Entry(frm_top, width=30)
        self.entry_dre_nome.grid(row=0, column=1, padx=4, pady=2)

        ttk.Label(frm_top, text="Campo DRE (mapear):").grid(row=0, column=2, sticky="w", padx=4, pady=2)
        dre_opcoes = [
            ("Receita Bruta", "receita_bruta"),
            ("Impostos", "impostos"),
            ("Custo", "custo"),
            ("Despesas Administrativas", "despesas_administrativas"),
            ("Distribuição de Lucro", "distribuicao_lucro"),
            ("Investimento", "investimento"),
            ("Empréstimos", "emprestimos")
        ]
        self.dre_field_map = {label: key for label, key in dre_opcoes}
        self.combo_dre_field = ttk.Combobox(frm_top, values=[label for label, _ in dre_opcoes], state="readonly", width=25)
        self.combo_dre_field.grid(row=0, column=3, padx=4, pady=2)
        self.combo_dre_field.set("Receita Bruta")

        ttk.Label(frm_top, text="Tipo:").grid(row=0, column=4, sticky="w", padx=4, pady=2)
        self.combo_dre_tipo = ttk.Combobox(frm_top, values=["receita", "despesa", "outro"], state="readonly", width=12)
        self.combo_dre_tipo.grid(row=0, column=5, padx=4, pady=2)
        self.combo_dre_tipo.set("receita")

        btn_frame = ttk.Frame(frm_top)
        btn_frame.grid(row=0, column=6, padx=6)
        ttk.Button(btn_frame, text="Adicionar", command=self._acao_adicionar_conta_dre).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Editar Selecionada", command=self._acao_editar_conta_dre).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Excluir Selecionada", command=self._acao_excluir_conta_dre).pack(side="left", padx=4)

        # Grid de contas DRE
        cols = ("ID", "Nome", "Campo DRE", "Tipo")
        self.tree_contas_dre = ttk.Treeview(f, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree_contas_dre.heading(c, text=c)
            if c == "Nome":
                self.tree_contas_dre.column(c, width=180)
            else:
                self.tree_contas_dre.column(c, width=80, anchor="center")
        self.tree_contas_dre.pack(fill="both", expand=True, pady=8)

    def _acao_adicionar_conta_dre(self):
        nome = self.entry_dre_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Preencha o nome da conta DRE.")
            return
        field_label = self.combo_dre_field.get()
        dre_field = self.dre_field_map.get(field_label, "receita_bruta")
        tipo = self.combo_dre_tipo.get() or "receita"
        
        # Determinar tipo baseado na operação (subtração para despesa, adição para receita)
        if dre_field in ["impostos", "custo", "despesas_administrativas", "distribuicao_lucro"]:
            tipo = "despesa"
        elif dre_field in ["receita_bruta", "investimento", "emprestimos"]:
            tipo = "receita" if dre_field == "receita_bruta" else "outro"

        self.sistema.adicionar_conta_dre(nome, dre_field, tipo)
        self.entry_dre_nome.delete(0, tk.END)
        self.atualizar_contas_dre_view()

    def _acao_editar_conta_dre(self):
        sel = self.tree_contas_dre.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecione a conta DRE a editar.")
            return
        item = self.tree_contas_dre.item(sel[0])["values"]
        conta_id = int(item[0])
        c = self.sistema.get_conta_dre(conta_id)
        if not c:
            return

        def salvar_edicao():
            novo_nome = entry_nome.get().strip()
            novo_field_label = combo_field.get()
            novo_field = self.dre_field_map.get(novo_field_label, c.dre_field)
            novo_tipo = combo_tipo.get()
            
            # Determinar tipo baseado na operação (subtração para despesa, adição para receita)
            if novo_field in ["impostos", "custo", "despesas_administrativas", "distribuicao_lucro"]:
                novo_tipo = "despesa"
            elif novo_field in ["receita_bruta", "investimento", "emprestimos"]:
                novo_tipo = "receita" if novo_field == "receita_bruta" else "outro"

            if not novo_nome:
                messagebox.showwarning("Atenção", "Nome não pode ficar vazio.")
                return

            self.sistema.atualizar_conta_dre(c.id, novo_nome, novo_field, novo_tipo)
            dlg.destroy()
            self.atualizar_contas_dre_view()
            self.atualizar_todas_views()

        dlg = tk.Toplevel(self)
        dlg.title("Editar Conta DRE")
        dlg.geometry("400x200")
        
        ttk.Label(dlg, text="Nome:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        entry_nome = ttk.Entry(dlg, width=40)
        entry_nome.grid(row=0, column=1, padx=6, pady=6)
        entry_nome.insert(0, c.nome)
        
        ttk.Label(dlg, text="Campo DRE:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        combo_field = ttk.Combobox(dlg, values=list(self.dre_field_map.keys()), state="readonly", width=36)
        combo_field.grid(row=1, column=1, padx=6, pady=6)
        inv_map = {v: k for k, v in self.dre_field_map.items()}
        combo_field.set(inv_map.get(c.dre_field, list(self.dre_field_map.keys())[0]))
        
        ttk.Label(dlg, text="Tipo:").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        combo_tipo = ttk.Combobox(dlg, values=["receita", "despesa", "outro"], state="readonly", width=36)
        combo_tipo.grid(row=2, column=1, padx=6, pady=6)
        combo_tipo.set(c.tipo)
        
        ttk.Button(dlg, text="Salvar", command=salvar_edicao).grid(row=3, column=0, columnspan=2, pady=10)

    def _acao_excluir_conta_dre(self):
        sel = self.tree_contas_dre.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecione a conta DRE a excluir.")
            return
        item = self.tree_contas_dre.item(sel[0])["values"]
        conta_id = int(item[0])
        ok = self.sistema.remover_conta_dre(conta_id)
        if not ok:
            messagebox.showerror("Erro", "Não é possível excluir uma conta DRE que está sendo usada por lançamentos.")
            return
        self.atualizar_contas_dre_view()
        self.atualizar_todas_views()

    # ---------------- Gerenciar Bancos ----------------
    def _construir_tab_bancos(self):
        f = ttk.Frame(self.tab_bancos, padding=8)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Gerenciar Bancos", font=("Arial", 14, "bold")).pack(anchor="w", pady=6)

        # Formulário para adicionar bancos
        frm_top = ttk.Frame(f)
        frm_top.pack(fill="x", pady=6)

        ttk.Label(frm_top, text="Nome do Banco:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.entry_banco_nome = ttk.Entry(frm_top, width=30)
        self.entry_banco_nome.grid(row=0, column=1, padx=4, pady=2)

        btn_frame = ttk.Frame(frm_top)
        btn_frame.grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="Adicionar Banco", command=self._acao_adicionar_banco).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Excluir Selecionado", command=self._acao_excluir_banco).pack(side="left", padx=4)

        # Lista de bancos
        self.lista_bancos = tk.Listbox(f, height=15)
        self.lista_bancos.pack(fill="both", expand=True, pady=8)

        # Atualizar lista
        self.atualizar_lista_bancos()

    def _acao_adicionar_banco(self):
        nome = self.entry_banco_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Preencha o nome do banco.")
            return
        
        if self.sistema.adicionar_banco(nome):
            self.entry_banco_nome.delete(0, tk.END)
            self.atualizar_lista_bancos()
            self.atualizar_comboboxes_bancos()
            messagebox.showinfo("Sucesso", "Banco adicionado com sucesso!")
        else:
            messagebox.showwarning("Atenção", "Este banco já existe.")

    def _acao_excluir_banco(self):
        selecionados = self.lista_bancos.curselection()
        if not selecionados:
            messagebox.showinfo("Info", "Selecione um banco para excluir.")
            return
        
        banco = self.lista_bancos.get(selecionados[0])
        
        # Verificar se o banco está sendo usado em algum lançamento
        for lanc in self.sistema.lancamentos:
            if lanc.conta_banco == banco:
                messagebox.showerror("Erro", f"O banco '{banco}' está sendo usado em lançamentos e não pode ser excluído.")
                return
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir o banco '{banco}'?"):
            if self.sistema.remover_banco(banco):
                self.atualizar_lista_bancos()
                self.atualizar_comboboxes_bancos()
                messagebox.showinfo("Sucesso", "Banco excluído com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao excluir banco.")

    def atualizar_lista_bancos(self):
        self.lista_bancos.delete(0, tk.END)
        for banco in self.sistema.obter_bancos():
            self.lista_bancos.insert(tk.END, banco)

    def atualizar_comboboxes_bancos(self):
        """Atualiza os comboboxes de bancos nas abas de lançamentos"""
        bancos = self.sistema.obter_bancos()
        if hasattr(self, 'entries_receber') and "Conta/Banco" in self.entries_receber:
            self.entries_receber["Conta/Banco"]['values'] = bancos
        if hasattr(self, 'entries_pagar') and "Conta/Banco" in self.entries_pagar:
            self.entries_pagar["Conta/Banco"]['values'] = bancos

    # ---------------- Gerenciar Categorias ----------------
    def _construir_tab_categorias(self):
        f = ttk.Frame(self.tab_categorias, padding=8)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Gerenciar Categorias", font=("Arial", 14, "bold")).pack(anchor="w", pady=6)

        # Formulário para adicionar categorias
        frm_top = ttk.Frame(f)
        frm_top.pack(fill="x", pady=6)

        ttk.Label(frm_top, text="Nome da Categoria:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.entry_categoria_nome = ttk.Entry(frm_top, width=30)
        self.entry_categoria_nome.grid(row=0, column=1, padx=4, pady=2)

        btn_frame = ttk.Frame(frm_top)
        btn_frame.grid(row=0, column=2, padx=6)
        ttk.Button(btn_frame, text="Adicionar Categoria", command=self._acao_adicionar_categoria).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Excluir Selecionada", command=self._acao_excluir_categoria).pack(side="left", padx=4)

        # Lista de categorias
        self.lista_categorias = tk.Listbox(f, height=15)
        self.lista_categorias.pack(fill="both", expand=True, pady=8)

        # Atualizar lista
        self.atualizar_lista_categorias()

    def _acao_adicionar_categoria(self):
        nome = self.entry_categoria_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Preencha o nome da categoria.")
            return
        
        if self.sistema.adicionar_categoria(nome):
            self.entry_categoria_nome.delete(0, tk.END)
            self.atualizar_lista_categorias()
            self.atualizar_comboboxes_categorias()
            messagebox.showinfo("Sucesso", "Categoria adicionada com sucesso!")
        else:
            messagebox.showwarning("Atenção", "Esta categoria já existe.")

    def _acao_excluir_categoria(self):
        selecionados = self.lista_categorias.curselection()
        if not selecionados:
            messagebox.showinfo("Info", "Selecione uma categoria para excluir.")
            return
        
        categoria = self.lista_categorias.get(selecionados[0])
        
        # Verificar se a categoria está sendo usada em algum lançamento
        for lanc in self.sistema.lancamentos:
            if lanc.categoria_texto == categoria:
                messagebox.showerror("Erro", f"A categoria '{categoria}' está sendo usada em lançamentos e não pode ser excluída.")
                return
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente excluir a categoria '{categoria}'?"):
            if self.sistema.remover_categoria(categoria):
                self.atualizar_lista_categorias()
                self.atualizar_comboboxes_categorias()
                messagebox.showinfo("Sucesso", "Categoria excluída com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao excluir categoria.")

    def atualizar_lista_categorias(self):
        self.lista_categorias.delete(0, tk.END)
        for categoria in self.sistema.obter_categorias():
            self.lista_categorias.insert(tk.END, categoria)

    def atualizar_comboboxes_categorias(self):
        """Atualiza os comboboxes de categorias nas abas de lançamentos"""
        categorias = self.sistema.obter_categorias()
        if hasattr(self, 'entries_receber') and "Categoria" in self.entries_receber:
            self.entries_receber["Categoria"]['values'] = categorias
        if hasattr(self, 'entries_pagar') and "Categoria" in self.entries_pagar:
            self.entries_pagar["Categoria"]['values'] = categorias

    # ---------------- Lancamentos (Receber / Pagar) ----------------
    def _construir_tab_lancamentos(self, parent, tipo):
        f = ttk.Frame(parent, padding=8)
        f.pack(fill="both", expand=True)

        titulo = "Contas a Receber" if tipo == "receber" else "Contas a Pagar"
        ttk.Label(f, text=titulo, font=("Arial", 14, "bold")).pack(anchor="w", pady=6)

        # Frame para filtros
        frame_filtros = ttk.Frame(f)
        frame_filtros.pack(fill="x", pady=10)

        # Filtro de data
        ttk.Label(frame_filtros, text="Data Início:").grid(row=0, column=0, padx=5)
        entry_data_inicio = ttk.Entry(frame_filtros, width=12)
        entry_data_inicio.grid(row=0, column=1, padx=5)
        entry_data_inicio.insert(0, self._get_primeiro_dia_mes_atual())
        self._bind_mascaras_em_entry(entry_data_inicio, "data")

        ttk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=2, padx=5)
        entry_data_fim = ttk.Entry(frame_filtros, width=12)
        entry_data_fim.grid(row=0, column=3, padx=5)
        entry_data_fim.insert(0, self._get_ultimo_dia_mes_atual())
        self._bind_mascaras_em_entry(entry_data_fim, "data")

        # Filtro de categoria
        ttk.Label(frame_filtros, text="Categoria:").grid(row=0, column=4, padx=5)
        combo_categoria_filtro = ttk.Combobox(frame_filtros, values=["Todas"] + self.sistema.obter_categorias(), state="readonly", width=15)
        combo_categoria_filtro.grid(row=0, column=5, padx=5)
        combo_categoria_filtro.set("Todas")

        # Filtro de banco
        ttk.Label(frame_filtros, text="Banco:").grid(row=0, column=6, padx=5)
        combo_banco_filtro = ttk.Combobox(frame_filtros, values=["Todos"] + self.sistema.obter_bancos(), state="readonly", width=15)
        combo_banco_filtro.grid(row=0, column=7, padx=5)
        combo_banco_filtro.set("Todos")

        # Filtro de status
        ttk.Label(frame_filtros, text="Status:").grid(row=0, column=8, padx=5)
        status_opcoes = ["Todos", "Pendente", "Recebido"] if tipo == "receber" else ["Todos", "Pendente", "Pago"]
        combo_status_filtro = ttk.Combobox(frame_filtros, values=status_opcoes, state="readonly", width=12)
        combo_status_filtro.grid(row=0, column=9, padx=5)
        combo_status_filtro.set("Todos")

        # Botão aplicar filtros
        btn_aplicar_filtros = ttk.Button(frame_filtros, text="Aplicar Filtros", 
                                       command=lambda: self._aplicar_filtros_lancamentos(tipo, entry_data_inicio.get(), entry_data_fim.get(), 
                                                                                       combo_categoria_filtro.get(), combo_banco_filtro.get(), 
                                                                                       combo_status_filtro.get()))
        btn_aplicar_filtros.grid(row=0, column=10, padx=10)

        # Armazenar referências aos filtros
        if tipo == "receber":
            self.filtros_receber = {
                'data_inicio': entry_data_inicio,
                'data_fim': entry_data_fim,
                'categoria': combo_categoria_filtro,
                'banco': combo_banco_filtro,
                'status': combo_status_filtro
            }
        else:
            self.filtros_pagar = {
                'data_inicio': entry_data_inicio,
                'data_fim': entry_data_fim,
                'categoria': combo_categoria_filtro,
                'banco': combo_banco_filtro,
                'status': combo_status_filtro
            }

        # Form de entrada
        form = ttk.Frame(f)
        form.pack(fill="x", pady=6)

        labels = [
            "Data Vencimento", "Cliente/Fornecedor", "Descrição", "Valor",
            "Status", "Data Baixa", "Conta/Banco", "Conta DRE", "Categoria"
        ]
        
        entries_local = {}
        data_baixa_entry = None
        
        for i, lbl in enumerate(labels):
            ttk.Label(form, text=f"{lbl} (DD/MM/AAAA)" if "Data" in lbl else lbl).grid(row=0, column=i, sticky="w", padx=4)
            
            if lbl == "Status":
                opts = ["Pendente", "Recebido"] if tipo == "receber" else ["Pendente", "Pago"]
                cb = ttk.Combobox(form, values=opts, state="readonly", width=14)
                cb.set(opts[0])
                cb.grid(row=1, column=i, padx=4, pady=4)
                entries_local["status"] = cb
                
            elif lbl == "Conta DRE":
                # Usar contas filtradas por tipo
                contas_filtradas = self._get_contas_dre_filtradas(tipo)
                combo = ttk.Combobox(form, values=contas_filtradas, state="readonly", width=28)
                if combo['values']:
                    combo.set(combo['values'][0])
                combo.grid(row=1, column=i, padx=4, pady=4)
                entries_local["conta_dre"] = combo
                
            elif lbl == "Conta/Banco":
                # Combobox para selecionar banco (apenas leitura)
                combo = ttk.Combobox(form, values=self.sistema.obter_bancos(), state="readonly", width=18)
                combo.grid(row=1, column=i, padx=4, pady=4)
                if combo['values']:
                    combo.set(combo['values'][0])
                entries_local["Conta/Banco"] = combo
                
            elif lbl == "Categoria":
                # Combobox para selecionar categoria (apenas leitura)
                combo = ttk.Combobox(form, values=self.sistema.obter_categorias(), state="readonly", width=18)
                combo.grid(row=1, column=i, padx=4, pady=4)
                if combo['values']:
                    combo.set(combo['values'][0])
                entries_local["Categoria"] = combo
                
            else:
                e = ttk.Entry(form, width=20 if i < 4 else 18)
                e.grid(row=1, column=i, padx=4, pady=4)
                
                key = lbl
                entries_local[key] = e

                if "Data" in lbl:
                    self._bind_mascaras_em_entry(e, "data")
                    if lbl == "Data Baixa":
                        data_baixa_entry = e
                if lbl == "Valor":
                    e.insert(0, "0,00")
                    self._bind_mascaras_em_entry(e, "valor")

        # Vincular evento de status change
        if "status" in entries_local and data_baixa_entry:
            def on_status_change(event):
                if entries_local["status"].get() in ["Recebido", "Pago"]:
                    if not data_baixa_entry.get().strip():
                        data_baixa_entry.delete(0, tk.END)
                        data_baixa_entry.insert(0, self._get_data_atual())
                else:
                    data_baixa_entry.delete(0, tk.END)
            
            entries_local["status"].bind('<<ComboboxSelected>>', on_status_change)

        if tipo == "receber":
            self.entries_receber = entries_local
        else:
            self.entries_pagar = entries_local

        # Botões
        btns = ttk.Frame(f)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Adicionar Lançamento", 
                  command=lambda: self._acao_adicionar_lancamento(tipo)).pack(side="left", padx=4)
        ttk.Button(btns, text="Editar Selecionado", 
                  command=lambda: self._acao_editar_lancamento(tipo)).pack(side="left", padx=4)
        ttk.Button(btns, text="Excluir Selecionado", 
                  command=lambda: self._acao_excluir_lancamento(tipo)).pack(side="left", padx=4)
        ttk.Button(btns, text="Baixar (Receber/Pagar)", 
                  command=lambda: self._acao_baixar_lancamento(tipo)).pack(side="left", padx=4)

        # Grid de lançamentos
        cols = ("ID", "Vencimento", "Entidade", "Descrição", "Valor", "Status", "Baixa", "Banco", "Conta DRE", "Categoria")
        if tipo == "receber":
            self.tree_receber = ttk.Treeview(f, columns=cols, show="headings", height=15)
            tree = self.tree_receber
        else:
            self.tree_pagar = ttk.Treeview(f, columns=cols, show="headings", height=15)
            tree = self.tree_pagar
        
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor="center")
        tree.column("Descrição", width=150)
        tree.column("Entidade", width=120)
        tree.column("Conta DRE", width=150)
        
        tree.pack(fill="both", expand=True, pady=8)

    def _aplicar_filtros_lancamentos(self, tipo, data_inicio, data_fim, categoria, banco, status):
        tree = self.tree_receber if tipo == "receber" else self.tree_pagar
        tree.delete(*tree.get_children())
        
        # Converter datas para datetime se fornecidas
        data_inicio_dt = None
        data_fim_dt = None
        
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%d/%m/%Y')
            except ValueError:
                messagebox.showerror("Erro", "Data início inválida")
                return
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%d/%m/%Y')
            except ValueError:
                messagebox.showerror("Erro", "Data fim inválida")
                return

        for l in self.sistema.lancamentos:
            if l.tipo == tipo:
                # Aplicar filtros
                if categoria != "Todas" and l.categoria_texto != categoria:
                    continue
                    
                if banco != "Todos" and l.conta_banco != banco:
                    continue
                    
                if status != "Todos" and l.status != status:
                    continue
                
                # Filtro de data (por data de vencimento)
                if data_inicio_dt and data_fim_dt:
                    try:
                        data_venc_dt = datetime.strptime(l.data_vencimento, '%d/%m/%Y')
                        if data_venc_dt < data_inicio_dt or data_venc_dt > data_fim_dt:
                            continue
                    except ValueError:
                        continue
                
                # Buscar nome da conta DRE
                conta_nome = ""
                if l.conta_dre_id:
                    conta = self.sistema.get_conta_dre(l.conta_dre_id)
                    if conta:
                        conta_nome = conta.nome
                
                tree.insert("", "end", values=(
                    l.id, l.data_vencimento, l.entidade, l.descricao,
                    f"R$ {l.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                    l.status, l.data_baixa, l.conta_banco, conta_nome, l.categoria_texto
                ))

    def _acao_adicionar_lancamento(self, tipo):
        entries = self.entries_receber if tipo == "receber" else self.entries_pagar
        
        # Obter dados dos campos
        data_vencimento = entries["Data Vencimento"].get().strip()
        entidade = entries["Cliente/Fornecedor"].get().strip()
        descricao = entries["Descrição"].get().strip()
        valor_texto = entries["Valor"].get().replace('.', '').replace(',', '.').strip()
        status = entries["status"].get()
        data_baixa = entries["Data Baixa"].get().strip()
        conta_banco = entries["Conta/Banco"].get().strip()
        conta_dre_texto = entries["conta_dre"].get()
        categoria_texto = entries["Categoria"].get().strip()

        # Validações
        if not all([data_vencimento, entidade, descricao]):
            messagebox.showwarning("Atenção", "Preencha Data Vencimento, Cliente/Fornecedor e Descrição.")
            return
        
        try:
            valor = float(valor_texto)
            if valor <= 0:
                raise ValueError("Valor deve ser positivo")
        except ValueError:
            messagebox.showwarning("Atenção", "Valor inválido.")
            return

        # Validar data de baixa baseado no status
        if status == "Pendente" and data_baixa.strip():
            messagebox.showwarning("Atenção", "Para status 'Pendente', a data de baixa não pode ser preenchida.")
            return
            
        if status in ["Recebido", "Pago"] and not data_baixa.strip():
            messagebox.showwarning("Atenção", f"Para status '{status}', a data de baixa é obrigatória.")
            return

        # Extrair ID da conta DRE usando o método auxiliar
        conta_dre_id = self._extrair_id_conta_dre(conta_dre_texto)

        # Adicionar lançamento
        lanc = self.sistema.adicionar_lancamento(
            tipo, data_vencimento, entidade, descricao, valor, 
            status, data_baixa, conta_banco, conta_dre_id, categoria_texto
        )
        
        if lanc is None:
            return  # Lançamento não foi adicionado devido a validação
        
        # Limpar campos
        for key, entry in entries.items():
            if key not in ["status", "conta_dre", "Conta/Banco", "Categoria"] and hasattr(entry, 'delete'):
                entry.delete(0, tk.END)
                if key == "Valor":
                    entry.insert(0, "0,00")
                if key == "Data Baixa":
                    # Manter data de baixa em branco para novos lançamentos
                    entry.delete(0, tk.END)
        
        self.atualizar_lancamentos_view(tipo)
        self.atualizar_todas_views()
        messagebox.showinfo("Sucesso", "Lançamento adicionado com sucesso!")

    def _acao_editar_lancamento(self, tipo):
        tree = self.tree_receber if tipo == "receber" else self.tree_pagar
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecione um lançamento para editar.")
            return
        
        item = tree.item(sel[0])["values"]
        lanc_id = int(item[0])
        
        # Buscar lançamento
        lanc = None
        for l in self.sistema.lancamentos:
            if l.id == lanc_id:
                lanc = l
                break
        
        if not lanc:
            messagebox.showerror("Erro", "Lançamento não encontrado.")
            return

        def salvar_edicao():
            # Obter novos valores
            nova_data_vencimento = entry_data_vencimento.get().strip()
            nova_entidade = entry_entidade.get().strip()
            nova_descricao = entry_descricao.get().strip()
            novo_valor_texto = entry_valor.get().replace('.', '').replace(',', '.').strip()
            novo_status = combo_status.get()
            nova_data_baixa = entry_data_baixa.get().strip()
            nova_conta_banco = combo_conta_banco.get().strip()
            nova_conta_dre_texto = combo_conta_dre.get()
            nova_categoria_texto = combo_categoria.get().strip()

            # Validações
            if not all([nova_data_vencimento, nova_entidade, nova_descricao]):
                messagebox.showwarning("Atenção", "Preencha Data Vencimento, Cliente/Fornecedor e Descrição.")
                return
            
            try:
                novo_valor = float(novo_valor_texto)
                if novo_valor <= 0:
                    raise ValueError("Valor deve ser positivo")
            except ValueError:
                messagebox.showwarning("Atenção", "Valor inválido.")
                return

            # Validar data de baixa baseado no status
            if novo_status == "Pendente" and nova_data_baixa.strip():
                messagebox.showwarning("Atenção", "Para status 'Pendente', a data de baixa não pode ser preenchida.")
                return
                
            if novo_status in ["Recebido", "Pago"] and not nova_data_baixa.strip():
                messagebox.showwarning("Atenção", f"Para status '{novo_status}', a data de baixa é obrigatória.")
                return

            # Extrair ID da conta DRE
            nova_conta_dre_id = self._extrair_id_conta_dre(nova_conta_dre_texto)

            # Atualizar lançamento
            success = self.sistema.atualizar_lancamento(
                lanc_id,
                data_vencimento=nova_data_vencimento,
                entidade=nova_entidade,
                descricao=nova_descricao,
                valor=novo_valor,
                status=novo_status,
                data_baixa=nova_data_baixa,
                conta_banco=nova_conta_banco,
                conta_dre_id=nova_conta_dre_id,
                categoria_texto=nova_categoria_texto
            )
            
            if success:
                dlg.destroy()
                self.atualizar_lancamentos_view(tipo)
                self.atualizar_todas_views()
                messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao atualizar lançamento.")

        # Diálogo de edição
        dlg = tk.Toplevel(self)
        dlg.title(f"Editar Lançamento - {tipo.title()}")
        dlg.geometry("500x400")
        
        # Campos do formulário
        ttk.Label(dlg, text="Data Vencimento:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        entry_data_vencimento = ttk.Entry(dlg, width=20)
        entry_data_vencimento.grid(row=0, column=1, padx=6, pady=6)
        entry_data_vencimento.insert(0, lanc.data_vencimento)
        self._bind_mascaras_em_entry(entry_data_vencimento, "data")
        
        ttk.Label(dlg, text="Cliente/Fornecedor:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        entry_entidade = ttk.Entry(dlg, width=20)
        entry_entidade.grid(row=1, column=1, padx=6, pady=6)
        entry_entidade.insert(0, lanc.entidade)
        
        ttk.Label(dlg, text="Descrição:").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        entry_descricao = ttk.Entry(dlg, width=20)
        entry_descricao.grid(row=2, column=1, padx=6, pady=6)
        entry_descricao.insert(0, lanc.descricao)
        
        ttk.Label(dlg, text="Valor:").grid(row=3, column=0, padx=6, pady=6, sticky="w")
        entry_valor = ttk.Entry(dlg, width=20)
        entry_valor.grid(row=3, column=1, padx=6, pady=6)
        entry_valor.insert(0, f"{lanc.valor:.2f}".replace('.', ','))
        self._bind_mascaras_em_entry(entry_valor, "valor")
        
        ttk.Label(dlg, text="Status:").grid(row=4, column=0, padx=6, pady=6, sticky="w")
        # Para contas a receber, remover opção "Pago"; para contas a pagar, remover opção "Recebido"
        if tipo == "receber":
            status_opcoes = ["Pendente", "Recebido"]
        else:
            status_opcoes = ["Pendente", "Pago"]
            
        combo_status = ttk.Combobox(dlg, values=status_opcoes, state="readonly", width=17)
        combo_status.grid(row=4, column=1, padx=6, pady=6)
        combo_status.set(lanc.status)
        
        ttk.Label(dlg, text="Data Baixa:").grid(row=5, column=0, padx=6, pady=6, sticky="w")
        entry_data_baixa = ttk.Entry(dlg, width=20)
        entry_data_baixa.grid(row=5, column=1, padx=6, pady=6)
        entry_data_baixa.insert(0, lanc.data_baixa)
        self._bind_mascaras_em_entry(entry_data_baixa, "data")
        
        ttk.Label(dlg, text="Conta/Banco:").grid(row=6, column=0, padx=6, pady=6, sticky="w")
        combo_conta_banco = ttk.Combobox(dlg, values=self.sistema.obter_bancos(), state="readonly", width=17)
        combo_conta_banco.grid(row=6, column=1, padx=6, pady=6)
        combo_conta_banco.set(lanc.conta_banco)
        
        ttk.Label(dlg, text="Conta DRE:").grid(row=7, column=0, padx=6, pady=6, sticky="w")
        # Usar contas filtradas por tipo
        contas_filtradas = self._get_contas_dre_filtradas(tipo)
        combo_conta_dre = ttk.Combobox(dlg, values=contas_filtradas, state="readonly", width=17)
        combo_conta_dre.grid(row=7, column=1, padx=6, pady=6)
        # Selecionar conta atual
        conta_atual = None
        if lanc.conta_dre_id:
            conta_atual = self.sistema.get_conta_dre(lanc.conta_dre_id)
        if conta_atual:
            combo_conta_dre.set(f"{conta_atual.id} - {conta_atual.nome}")
        elif combo_conta_dre['values']:
            combo_conta_dre.set(combo_conta_dre['values'][0])
        
        ttk.Label(dlg, text="Categoria:").grid(row=8, column=0, padx=6, pady=6, sticky="w")
        combo_categoria = ttk.Combobox(dlg, values=self.sistema.obter_categorias(), state="readonly", width=17)
        combo_categoria.grid(row=8, column=1, padx=6, pady=6)
        combo_categoria.set(lanc.categoria_texto)
        
        ttk.Button(dlg, text="Salvar", command=salvar_edicao).grid(row=9, column=0, columnspan=2, pady=20)

    def _acao_excluir_lancamento(self, tipo):
        tree = self.tree_receber if tipo == "receber" else self.tree_pagar
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecione um lançamento para excluir.")
            return
        
        item = tree.item(sel[0])["values"]
        lanc_id = int(item[0])
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este lançamento?"):
            success = self.sistema.remover_lancamento(lanc_id)
            if success:
                self.atualizar_lancamentos_view(tipo)
                self.atualizar_todas_views()
                messagebox.showinfo("Sucesso", "Lançamento excluído com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao excluir lançamento.")

    def _acao_baixar_lancamento(self, tipo):
        tree = self.tree_receber if tipo == "receber" else self.tree_pagar
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecione um lançamento para baixar.")
            return
        
        item = tree.item(sel[0])["values"]
        lanc_id = int(item[0])
        
        # Buscar lançamento
        lanc = None
        for l in self.sistema.lancamentos:
            if l.id == lanc_id:
                lanc = l
                break
        
        if not lanc:
            messagebox.showerror("Erro", "Lançamento não encontrado.")
            return
        
        novo_status = "Recebido" if tipo == "receber" else "Pago"
        
        if lanc.status == novo_status:
            messagebox.showinfo("Info", f"Lançamento já está {novo_status.lower()}.")
            return
        
        success = self.sistema.atualizar_lancamento(
            lanc_id,
            status=novo_status,
            data_baixa=self._get_data_atual()
        )
        
        if success:
            self.atualizar_lancamentos_view(tipo)
            self.atualizar_todas_views()
            messagebox.showinfo("Sucesso", f"Lançamento baixado como {novo_status.lower()}!")
        else:
            messagebox.showerror("Erro", "Erro ao baixar lançamento.")

    # ---------------- DRE ----------------
    def _construir_dre(self):
        f = ttk.Frame(self.tab_dre, padding=20)
        f.pack(fill="both", expand=True)
        
        ttk.Label(f, text="Demonstrativo de Resultado do Exercício (DRE)", 
                 font=("Arial", 16, "bold")).pack(pady=10)

        # Filtros de data
        frame_filtros = ttk.Frame(f)
        frame_filtros.pack(pady=10)
        
        ttk.Label(frame_filtros, text="Data Início:").grid(row=0, column=0, padx=5)
        self.entry_dre_data_inicio = ttk.Entry(frame_filtros, width=12)
        self.entry_dre_data_inicio.grid(row=0, column=1, padx=5)
        # Definir data inicial como primeiro dia do mês atual
        self.entry_dre_data_inicio.insert(0, self._get_primeiro_dia_mes_atual())
        self._bind_mascaras_em_entry(self.entry_dre_data_inicio, "data")
        
        ttk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=2, padx=5)
        self.entry_dre_data_fim = ttk.Entry(frame_filtros, width=12)
        self.entry_dre_data_fim.grid(row=0, column=3, padx=5)
        # Definir data final como último dia do mês atual
        self.entry_dre_data_fim.insert(0, self._get_ultimo_dia_mes_atual())
        self._bind_mascaras_em_entry(self.entry_dre_data_fim, "data")
        
        ttk.Button(frame_filtros, text="Calcular DRE", command=self.atualizar_dre_view).grid(row=0, column=4, padx=10)

        # Frame para resultados
        frame_resultados = ttk.Frame(f)
        frame_resultados.pack(fill="both", expand=True, pady=10)
        
        # Treeview para DRE
        cols = ("Descrição", "Valor (R$)")
        self.tree_dre = ttk.Treeview(frame_resultados, columns=cols, show="headings", height=20)
        self.tree_dre.heading("Descrição", text="Descrição")
        self.tree_dre.heading("Valor (R$)", text="Valor (R$)")
        self.tree_dre.column("Descrição", width=300, anchor="w")
        self.tree_dre.column("Valor (R$)", width=200, anchor="e")
        self.tree_dre.pack(fill="both", expand=True)

    # ---------------- Fluxo de Caixa ----------------
    def _construir_tab_fluxo_caixa(self):
        f = ttk.Frame(self.tab_fluxo_caixa, padding=8)
        f.pack(fill="both", expand=True)

        titulo = "Fluxo de Caixa"
        ttk.Label(f, text=titulo, font=("Arial", 14, "bold")).pack(anchor="w", pady=6)

        # Frame para filtros
        frame_filtros = ttk.Frame(f)
        frame_filtros.pack(fill="x", pady=10)

        # Filtro de data
        ttk.Label(frame_filtros, text="Data Início:").grid(row=0, column=0, padx=5)
        self.entry_fluxo_data_inicio = ttk.Entry(frame_filtros, width=12)
        self.entry_fluxo_data_inicio.grid(row=0, column=1, padx=5)
        self.entry_fluxo_data_inicio.insert(0, self._get_primeiro_dia_mes_atual())
        self._bind_mascaras_em_entry(self.entry_fluxo_data_inicio, "data")

        ttk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=2, padx=5)
        self.entry_fluxo_data_fim = ttk.Entry(frame_filtros, width=12)
        self.entry_fluxo_data_fim.grid(row=0, column=3, padx=5)
        self.entry_fluxo_data_fim.insert(0, self._get_ultimo_dia_mes_atual())
        self._bind_mascaras_em_entry(self.entry_fluxo_data_fim, "data")

        # Filtro de categoria
        ttk.Label(frame_filtros, text="Categoria:").grid(row=0, column=4, padx=5)
        self.combo_fluxo_categoria = ttk.Combobox(frame_filtros, values=["Todas"] + self.sistema.obter_categorias(), state="readonly", width=15)
        self.combo_fluxo_categoria.grid(row=0, column=5, padx=5)
        self.combo_fluxo_categoria.set("Todas")

        # Filtro de banco
        ttk.Label(frame_filtros, text="Banco:").grid(row=0, column=6, padx=5)
        self.combo_fluxo_banco = ttk.Combobox(frame_filtros, values=["Todos"] + self.sistema.obter_bancos(), state="readonly", width=15)
        self.combo_fluxo_banco.grid(row=0, column=7, padx=5)
        self.combo_fluxo_banco.set("Todos")

        ttk.Button(frame_filtros, text="Aplicar Filtros", command=self.atualizar_fluxo_caixa_view).grid(row=0, column=8, padx=10)

        # Treeview para fluxo de caixa
        cols = ("Data", "Tipo", "Descrição", "Categoria", "Banco", "Entrada", "Saída", "Saldo")
        self.tree_fluxo_caixa = ttk.Treeview(f, columns=cols, show="headings", height=20)
        
        for c in cols:
            self.tree_fluxo_caixa.heading(c, text=c)
            self.tree_fluxo_caixa.column(c, width=100, anchor="center")
        
        self.tree_fluxo_caixa.column("Descrição", width=150)
        self.tree_fluxo_caixa.column("Data", width=100)
        
        self.tree_fluxo_caixa.pack(fill="both", expand=True, pady=8)

        # Labels totais
        frame_totais = ttk.Frame(f)
        frame_totais.pack(fill="x", pady=5)
        
        self.lbl_total_entradas = ttk.Label(frame_totais, text="Total Entradas: R$ 0,00", font=("Arial", 10, "bold"))
        self.lbl_total_entradas.pack(side="left", padx=10)
        
        self.lbl_total_saidas = ttk.Label(frame_totais, text="Total Saídas: R$ 0,00", font=("Arial", 10, "bold"))
        self.lbl_total_saidas.pack(side="left", padx=10)
        
        self.lbl_saldo_final = ttk.Label(frame_totais, text="Saldo Final: R$ 0,00", font=("Arial", 10, "bold"))
        self.lbl_saldo_final.pack(side="left", padx=10)

    def atualizar_fluxo_caixa_view(self):
        self.tree_fluxo_caixa.delete(*self.tree_fluxo_caixa.get_children())
        
        data_inicio = self.entry_fluxo_data_inicio.get().strip()
        data_fim = self.entry_fluxo_data_fim.get().strip()
        categoria_filtro = self.combo_fluxo_categoria.get()
        banco_filtro = self.combo_fluxo_banco.get()
        
        # Converter datas para datetime se fornecidas
        data_inicio_dt = None
        data_fim_dt = None
        
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%d/%m/%Y')
            except ValueError:
                messagebox.showerror("Erro", "Data início inválida")
                return
        
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%d/%m/%Y')
            except ValueError:
                messagebox.showerror("Erro", "Data fim inválida")
                return

        # Calcular fluxo
        lancamentos_fluxo = []
        saldo_atual = 0
        total_entradas = 0
        total_saidas = 0
        
        # Ordenar lançamentos por data de baixa (quando houver) ou data de vencimento
        lancamentos_ordenados = sorted(self.sistema.lancamentos, 
                                      key=lambda x: x.data_baixa if x.data_baixa else x.data_vencimento)
        
        for lanc in lancamentos_ordenados:
            # Aplicar filtros
            if categoria_filtro != "Todas" and lanc.categoria_texto != categoria_filtro:
                continue
                
            if banco_filtro != "Todos" and lanc.conta_banco != banco_filtro:
                continue
            
            # Determinar data para ordenação (priorizar data de baixa)
            data_lancamento = lanc.data_baixa if lanc.data_baixa else lanc.data_vencimento
            
            # Aplicar filtro de data se fornecido
            if data_inicio_dt and data_fim_dt:
                try:
                    data_lanc_dt = datetime.strptime(data_lancamento, '%d/%m/%Y')
                    if data_lanc_dt < data_inicio_dt or data_lanc_dt > data_fim_dt:
                        continue
                except ValueError:
                    continue
            
            # Calcular entradas e saídas
            entrada = 0
            saida = 0
            
            if lanc.tipo == "receber" and lanc.status == "Recebido":
                entrada = lanc.valor
                total_entradas += entrada
            elif lanc.tipo == "pagar" and lanc.status == "Pago":
                saida = lanc.valor
                total_saidas += saida
            else:
                # Pular lançamentos não baixados
                continue
            
            saldo_atual += entrada - saida
            
            # Adicionar ao treeview
            self.tree_fluxo_caixa.insert("", "end", values=(
                data_lancamento,
                "Receita" if lanc.tipo == "receber" else "Despesa",
                lanc.descricao,
                lanc.categoria_texto,
                lanc.conta_banco,
                f"R$ {entrada:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if entrada > 0 else "",
                f"R$ {saida:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if saida > 0 else "",
                f"R$ {saldo_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            ))
        
        # Atualizar totais
        self.lbl_total_entradas.config(text=f"Total Entradas: R$ {total_entradas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.lbl_total_saidas.config(text=f"Total Saídas: R$ {total_saidas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        saldo_final = total_entradas - total_saidas
        cor = "green" if saldo_final >= 0 else "red"
        self.lbl_saldo_final.config(
            text=f"Saldo Final: R$ {saldo_final:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            foreground=cor
        )

    # ---------------- Atualizações de View ----------------
    def atualizar_todas_views(self):
        # REMOVIDO: self.atualizar_dashboard_view()
        self.atualizar_contas_dre_view()
        self.atualizar_lancamentos_view("receber")
        self.atualizar_lancamentos_view("pagar")
        self.atualizar_dre_view()
        self.atualizar_fluxo_caixa_view()

    # REMOVIDO: Método atualizar_dashboard_view() completamente

    def atualizar_contas_dre_view(self):
        self.tree_contas_dre.delete(*self.tree_contas_dre.get_children())
        for c in self.sistema.contas_dre:
            self.tree_contas_dre.insert("", "end", values=(
                c.id, c.nome, c.dre_field, c.tipo
            ))

    def atualizar_lancamentos_view(self, tipo):
        # Se existirem filtros aplicados, use o método de filtros
        if hasattr(self, f'filtros_{tipo}'):
            filtros = getattr(self, f'filtros_{tipo}')
            self._aplicar_filtros_lancamentos(
                tipo, 
                filtros['data_inicio'].get(),
                filtros['data_fim'].get(),
                filtros['categoria'].get(),
                filtros['banco'].get(),
                filtros['status'].get()
            )
        else:
            # Comportamento original (sem filtros)
            tree = self.tree_receber if tipo == "receber" else self.tree_pagar
            tree.delete(*tree.get_children())
            
            for l in self.sistema.lancamentos:
                if l.tipo == tipo:
                    # Buscar nome da conta DRE
                    conta_nome = ""
                    if l.conta_dre_id:
                        conta = self.sistema.get_conta_dre(l.conta_dre_id)
                        if conta:
                            conta_nome = conta.nome
                    
                    tree.insert("", "end", values=(
                        l.id, l.data_vencimento, l.entidade, l.descricao,
                        f"R$ {l.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                        l.status, l.data_baixa, l.conta_banco, conta_nome, l.categoria_texto
                    ))

    def atualizar_dre_view(self):
        self.tree_dre.delete(*self.tree_dre.get_children())
        
        data_inicio = self.entry_dre_data_inicio.get().strip()
        data_fim = self.entry_dre_data_fim.get().strip()
        
        dre_vals = self.sistema.calcular_dre(data_inicio, data_fim)
        
        # Formatar e exibir resultados
        itens_dre = [
            ("Receita Bruta", dre_vals['receita_bruta']),
            ("(-) Impostos sobre Vendas", dre_vals['impostos']),
            ("(=) Receita Líquida", dre_vals['receita_liquida']),
            ("(-) Custo", dre_vals['custo']),  # Alterado de "Custo das Mercadorias Vendidas" para "Custo"
            ("(=) Lucro Bruto", dre_vals['lucro_bruto']),
            ("(-) Despesas Administrativas", dre_vals['despesas_administrativas']),
            ("(=) Resultado Operacional", dre_vals['resultado_operacional']),
            ("(+) Investimentos", dre_vals['investimento']),
            ("(+) Empréstimos", dre_vals['emprestimos']),
            ("(-) Distribuição de Lucro", dre_vals['distribuicao_lucro']),
            ("(=) Resultado do Período", dre_vals['resultado_periodo'])
        ]
        
        for descricao, valor in itens_dre:
            valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self.tree_dre.insert("", "end", values=(descricao, valor_formatado))

# -------------------------------
# Inicialização
# -------------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()