import re

# ==========================================
# 1. TAHAPAN LEKSIKAL (Lexical Analysis)
# ==========================================
TOKEN_TYPES = [
    ('KEYWORD', r'\b(if|else)\b'),
    ('ID', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('NUM', r'\b\d+\b'),
    ('OP', r'==|!=|<=|>=|<|>|='),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('SKIP', r'[ \t\n]+'),
]

def lexical_analyzer(code):
    tokens = []
    pos = 0
    while pos < len(code):
        match = None
        for token_type, regex in TOKEN_TYPES:
            match = re.match(regex, code[pos:])
            if match:
                text = match.group(0)
                if token_type != 'SKIP':
                    tokens.append((token_type, text))
                pos += len(text)
                break
        if not match:
            raise SyntaxError(f"Karakter ilegal ditemukan: {code[pos]}")
    return tokens


# ==========================================
# 2. TAHAPAN SINTAKSIS (Syntax Analysis / Parser)
# ==========================================
class ASTNode:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children if children else []

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def consume(self, expected_type):
        type, val = self.peek()
        if type == expected_type:
            self.pos += 1
            return val
        raise SyntaxError(f"Ekspektasi {expected_type}, tetapi menemukan {type}")

    def parse(self):
        # Memulai parsing konstruksi IF
        self.consume('KEYWORD')  # 'if'
        self.consume('LPAREN')
        
        # Kondisi: ID OP NUM (misal: x > 5)
        left = self.consume('ID')
        op = self.consume('OP')
        right = self.consume('NUM')
        cond_node = ASTNode('CONDITION', op, [ASTNode('ID', left), ASTNode('NUM', right)])
        
        self.consume('RPAREN')
        self.consume('LBRACE')
        
        # Statement True: ID = NUM atau ID = ID
        id_true = self.consume('ID')
        self.consume('OP')  # '='
        val_true = self.peek()[1]
        self.pos += 1 # consume value
        then_node = ASTNode('ASSIGN', '=', [ASTNode('ID', id_true), ASTNode('VAL', val_true)])
        
        self.consume('RBRACE')
        self.consume('KEYWORD')  # 'else'
        self.consume('LBRACE')
        
        # Statement False
        id_false = self.consume('ID')
        self.consume('OP')  # '='
        val_false = self.peek()[1]
        self.pos += 1
        else_node = ASTNode('ASSIGN', '=', [ASTNode('ID', id_false), ASTNode('VAL', val_false)])
        
        self.consume('RBRACE')
        
        return ASTNode('IF_STMT', None, [cond_node, then_node, else_node])


# ==========================================
# 3. TAHAPAN SEMANTIK (Semantic Analysis)
# ==========================================
# Simulasikan sebuah Symbol Table dengan tipe data variabel yang sudah dideklarasikan
SYMBOL_TABLE = {
    'x': 'int',
    'y': 'int',
    'z': 'string'  # z bertipe string untuk memicu error semantik jika dioperasi dengan angka
}

def semantic_analyzer(node):
    if node.type == 'IF_STMT':
        for child in node.children:
            semantic_analyzer(child)
            
    elif node.type == 'CONDITION':
        var_name = node.children[0].value
        if var_name not in SYMBOL_TABLE:
            raise NameError(f"Semantic Error: Variabel '{var_name}' belum dideklarasikan!")
            
    elif node.type == 'ASSIGN':
        var_name = node.children[0].value
        val_node = node.children[1]
        
        if var_name not in SYMBOL_TABLE:
            raise NameError(f"Semantic Error: Variabel '{var_name}' belum dideklarasikan!")
            
        # Aturan Semantik: Variabel 'int' tidak boleh di-assign nilai string/karakter non-angka
        if SYMBOL_TABLE[var_name] == 'int' and not val_node.value.isdigit():
            # Cek jika di-assign variabel lain yang tipenya berbeda
            if val_node.value in SYMBOL_TABLE and SYMBOL_TABLE[val_node.value] != 'int':
                raise TypeError(f"Type Error: Ketidakcocokan tipe data pada variabel '{var_name}'")


# ==========================================
# 4. GENERASI KODE ANTARA (Three-Address Code / TAC)
# ==========================================
label_counter = 0
def get_new_label():
    global label_counter
    label_counter += 1
    return f"L{label_counter}"

def generate_tac(node):
    if node.type == 'IF_STMT':
        cond_node, then_node, else_node = node.children
        
        label_true = get_new_label()
        label_false = get_new_label()
        label_end = get_new_label()
        
        # 1. Evaluasi Kondisi
        print(f"if {cond_node.children[0].value} {cond_node.value} {cond_node.children[1].value} goto {label_true}")
        print(f"goto {label_false}")
        
        # 2. Bagian True (Then)
        print(f"\n{label_true}:")
        print(f"    {then_node.children[0].value} = {then_node.children[1].value}")
        print(f"    goto {label_end}")
        
        # 3. Bagian False (Else)
        print(f"\n{label_false}:")
        print(f"    {else_node.children[0].value} = {else_node.children[1].value}")
        
        # 4. Akhir If
        print(f"\n{label_end}:")


# ==========================================
# RUNNING THE COMPILER PIPELINE
# ==========================================
if __name__ == "__main__":
    # Kode sumber inputan yang valid
    source_code = """
    if (x > 5) {
        y = 10
    } else {
        y = 20
    }
    """
    
    print("=== SOURCE CODE ===")
    print(source_code.strip())
    
    print("\n[1] HASIL ANALISIS LEKSIKAL (Tokens):")
    tokens = lexical_analyzer(source_code)
    print(tokens)
    
    print("\n[2] HASIL ANALISIS SINTAKSIS (AST):")
    parser = Parser(tokens)
    ast_root = parser.parse()
    print(f"Root: {ast_root.type}")
    print(f" └── Children 1 (Cond): {ast_root.children[0].type} ({ast_root.children[0].value})")
    print(f" └── Children 2 (Then): {ast_root.children[1].type}")
    print(f" └── Children 3 (Else): {ast_root.children[2].type}")
    
    print("\n[3] HASIL ANALISIS SEMANTIK:")
    try:
        semantic_analyzer(ast_root)
        print("Status: Valid (Tidak ada kesalahan semantik)")
    except Exception as e:
        print(e)
        
    print("\n[4] GENERASI KODE ANTARA (Three-Address Code):")
    generate_tac(ast_root)