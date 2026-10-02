from lark import Lark, Transformer, v_args

# =============================================================================
# 1. DEFINIÇÃO DA GRAMÁTICA (A "ESTRUTURA" DO CÓDIGO)
# =============================================================================
# Usamos a notação EBNF. Regras minúsculas geram árvores, MAIÚSCULAS geram texto.
gramatica_id = """
    # O ponto de entrada (root) da nossa linguagem. 
    # O '?' diz ao Lark: "se houver só 1 filho, não crie um nó extra na árvore".
    ?start: documento

    # A regra principal: um documento é composto por um ESTADO, um ":" e um NUMERO.
    documento: ESTADO ":" NUMERO
    
    # Terminais (Tokens):
    ESTADO: "SP" | "RJ"      // Aceita apenas as strings literais SP ou RJ
    NUMERO: /[0-9]+/         // Aceita um ou mais dígitos de 0 a 9
    
    # Importações e IGNORE:
    %import common.WS        // Importa a definição de espaços em branco (Whitespace)
    %ignore WS               // Ignora espaços entre os tokens (ex: "SP : 11")
"""

# =============================================================================
# 2. IMPLEMENTAÇÃO DO TRANSFORMER (A "INTELIGÊNCIA" / SEMÂNTICA)
# =============================================================================
# O Transformer percorre a árvore de baixo para cima, executando funções 
# que tenham o mesmo nome das regras da gramática.
class ValidadorCompliance(Transformer):
    
    # @v_args(inline=True) "desempacota" os filhos da regra 'documento'
    # transformando-os em argumentos diretos (estado, numero) da função.
    @v_args(inline=True)
    def documento(self, estado, numero):
        # Como ESTADO e NUMERO são terminais (maiúsculos), 
        # eles chegam aqui como objetos 'Token', que convertemos para String.
        sigla_estado = str(estado)
        num_completo = str(numero)
        
        # --- GRAMÁTICA SENSÍVEL AO CONTEXTO (GSC) ---
        # Aqui o valor de um campo (estado) valida o formato do outro (numero).
        
        # Verificação para São Paulo (Prefixo 11)
        if sigla_estado == "SP" and not num_completo.startswith("11"):
            return f"❌ ERRO DE COMPLIANCE: Estado SP não aceita prefixo {num_completo[:2]}"
        
        # Verificação para Rio de Janeiro (Prefixo 21)
        if sigla_estado == "RJ" and not num_completo.startswith("21"):
            return f"❌ ERRO DE COMPLIANCE: Estado RJ não aceita prefixo {num_completo[:2]}"
            
        # Se passar pelas validações, retorna a mensagem de sucesso
        return f"✅ SUCESSO: Documento {sigla_estado} válido com número {num_completo}"

    # O método 'start' recebe o resultado do seu único filho (documento)
    # e simplesmente o repassa para cima, limpando a saída final.
    def start(self, children):
        return children[0]

# =============================================================================
# 3. EXECUÇÃO E TESTES
# =============================================================================

# Inicializa o 'Motor' do Lark com a nossa gramática
parser = Lark(gramatica_id)

# Inicializa o nosso 'Fiscal' (Transformer)
validador = ValidadorCompliance()

# Função auxiliar para testar entradas e imprimir o resultado limpo
def testar(texto):
    # 1. O parser transforma o texto em uma Árvore de Sintaxe
    arvore_sintatica = parser.parse(texto)
    # 2. O validador percorre a árvore aplicando as regras lógicas
    resultado_final = validador.transform(arvore_sintatica)
    print(resultado_final)

# Execução dos testes práticos
print("--- RELATÓRIO DE VALIDAÇÃO ---")
testar("SP : 11999")   # Deve dar SUCESSO
testar("RJ : 21888")   # Deve dar SUCESSO
testar("SP : 21000")   # Deve dar ERRO (Prefixo do RJ em SP)
testar("RJ : 11000")   # Deve dar ERRO (Prefixo de SP no RJ)