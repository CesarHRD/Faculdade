from lark import Lark, Transformer

# =============================================================================
# 1. A GRAMÁTICA (SINTAXE - A FORMA)
# =============================================================================
# Aqui o Lark apenas verifica se o usuário escreveu as palavras corretamente 
# e na ordem certa. Ele NÃO sabe se a variável existe ou não.
gramatica_memoria = """
    # Regra inicial: o programa é composto por um ou mais comandos (+)
    ?start: programa
    programa: comando+
    
    # Define quais tipos de comandos nossa linguagem aceita
    ?comando: alloc_cmd | free_cmd | use_cmd
    
    # Estrutura específica de cada comando (Ex: ALLOC x;)
    alloc_cmd: "ALLOC" ID ";"
    free_cmd: "FREE" ID ";"
    use_cmd: "USE" ID ";"
    
    # Regra para identificadores (nomes de variáveis)
    # Deve começar com letra/underline e pode conter números
    ID: /[a-z_][a-z0-9_]*/
    
    # Ignora espaços, tabs e quebras de linha entre os comandos
    %import common.WS
    %ignore WS
"""

# =============================================================================
# 2. O TRANSFORMER (SEMÂNTICA/CONTEXTO - A INTELIGÊNCIA)
# =============================================================================
# Esta classe é o "cérebro" do compilador. Ela percorre a árvore gerada pelo 
# Lark e aplica as regras lógicas de Sensibilidade ao Contexto (GSC).
class GestorSemantico(Transformer):
    def __init__(self):
        # Nossa 'Tabela de Símbolos' simplificada. 
        # Um 'set' em Python é perfeito para rastrear o que está "vivo" na memória.
        self.variaveis_alocadas = set()

    # Executado sempre que o Lark encontra a regra 'alloc_cmd'
    def alloc_cmd(self, nodes):
        var_name = str(nodes[0]) # Pega o nome da variável (ID)
        if var_name in self.variaveis_alocadas:
            return f"⚠️ AVISO: Variável '{var_name}' já estava alocada. Reatribuindo..."
        
        self.variaveis_alocadas.add(var_name) # Adiciona ao contexto de 'vivas'
        return f"✅ SUCCESS: Memória reservada para '{var_name}'."

    # Executado sempre que o Lark encontra a regra 'free_cmd'
    def free_cmd(self, nodes):
        var_name = str(nodes[0])
        # VERIFICAÇÃO DE CONTEXTO: Só podemos liberar o que foi alocado antes!
        if var_name not in self.variaveis_alocadas:
            return f"❌ ERRO GSC: Tentativa de liberar '{var_name}' que NUNCA foi alocada!"
        
        self.variaveis_alocadas.remove(var_name) # Remove do contexto
        return f"🗑️ SUCCESS: Memória de '{var_name}' liberada."

    # Executado sempre que o Lark encontra a regra 'use_cmd'
    def use_cmd(self, nodes):
        var_name = str(nodes[0])
        # O "Segmentation Fault" ocorre quando acessamos algo que não está no contexto 'vivo'
        if var_name not in self.variaveis_alocadas:
            return f"🚨 ERRO CRÍTICO: 'Segmentation Fault' ao tentar usar '{var_name}'. Contexto inválido!"
        
        return f"💎 SUCCESS: Acessando valor de '{var_name}'."

    # Junta todos os resultados dos comandos em um relatório final legível
    def programa(self, comandos):
        return "\n".join(comandos)

# =============================================================================
# 3. EXECUÇÃO (O PROCESSO DE COMPILAÇÃO)
# =============================================================================

# Criamos o Analisador (Parser) usando a gramática definida
parser = Lark(gramatica_memoria)

# Criamos o Fiscal Semântico (Transformer)
gestor = GestorSemantico()

# Exemplo de código-fonte que será "mastigado" pelo nosso compilador
codigo_fonte = """
    ALLOC buffer;
    USE buffer;
    FREE buffer;
"""

try:
    # PASSO 1: Análise Sintática (Gera a Árvore)
    arvore = parser.parse(codigo_fonte)
    
    # PASSO 2: Análise Semântica (Transforma a Árvore em Resultados Lógicos)
    resultado = gestor.transform(arvore)
    
    print("--- RELATÓRIO DO COMPILADOR (UNIDADE 7) ---")
    print(resultado)
except Exception as e:
    # Captura erros de escrita (ex: faltou o ponto e vírgula)
    print(f"❌ Erro de Sintaxe (Escrita incorreta): {e}")