from lark import Lark, Transformer

# --- 1. GRAMÁTICA ---
gramatica_hdl = """
    ?start: comando
    
    # Um comando é a união de um estado de pino e uma ação de escrita
    comando: status_pino acao
    
    # Definimos os estados possíveis do hardware
    status_pino: "ENABLE:HIGH" -> liga
               | "ENABLE:LOW"  -> desliga
               
    # A ação de escrita no barramento
    acao: "WRITE" -> escrita
    
    %import common.WS
    %ignore WS
"""

# --- 2. TRANSFORMER (O FISCAL DE HARDWARE) ---
class VerificadorHDL(Transformer):
    # Esta variável guarda o estado "físico" simulado do pino
    def __init__(self):
        self.pino_ativado = False

    # Quando o Lark encontra "ENABLE:HIGH", ele chama esta função
    def liga(self, _):
        self.pino_ativado = True
        return "PINO: LIGADO"

    # Quando o Lark encontra "ENABLE:LOW", ele chama esta função
    def desliga(self, _):
        self.pino_ativado = False
        return "PINO: DESLIGADO"

    # Quando o Lark encontra "WRITE", ele chama esta função
    def escrita(self, _):
        return "OPERACAO: ESCREVER"

    # Esta função final une o contexto (pino) com a ação (escrita)
    def comando(self, children):
        # children[0] é o resultado de 'status_pino'
        # children[1] é o resultado de 'acao'
        
        if self.pino_ativado == False:
            return "❌ ERRO CRÍTICO: Tentativa de WRITE com ENABLE:LOW. Bloqueado para evitar curto-circuito!"
        
        return "✅ SUCESSO: Escrita realizada com segurança no barramento."

# --- 3. TESTES ---
hdl_parser = Lark(gramatica_hdl)
fiscal = VerificadorHDL()

# Teste 1: Caminho Seguro
print(fiscal.transform(hdl_parser.parse("ENABLE:HIGH WRITE")))

# Teste 2: Caminho Perigoso (O Compilador deve barrar)
# Reiniciamos o fiscal para o novo teste
fiscal = VerificadorHDL()
print(fiscal.transform(hdl_parser.parse("ENABLE:LOW WRITE")))