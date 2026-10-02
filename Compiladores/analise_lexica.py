from lark import Lark

# Definição da Gramática com foco no Léxico
# Usamos terminais em MAIÚSCULO para definir os Tokens
gramatica_lexica = """
    start: (TOKEN | OPERADOR | NUMERO)+

    # Definição de Tokens via Expressões Regulares
    TOKEN: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMERO: /[0-9]+/
    OPERADOR: "+" | "-" | "*" | "/" | "="

    # Tratamento de Ruídos
    %import common.WS
    %ignore WS  // Aqui o Lark descarta espaços automaticamente
"""

# Criando o Scanner
parser = Lark(gramatica_lexica)

# Testando a identificação de palavras
texto = "total = 50 + 5a"
tokens = parser.lex(texto)

print(f"Texto original: {texto}")
print("Tokens identificados:")
for t in tokens:
    print(f"Tipo: {t.type:10} | Valor: {t.value}")

