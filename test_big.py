import sys
import re
from functools import reduce

# ==========================================
# 0. Helper: 模擬 32-bit 溢位
# ==========================================
def to_int32(val):
    """將數值強制轉型為 32-bit signed integer"""
    val &= 0xFFFFFFFF
    if val > 0x7FFFFFFF:
        val -= 0x100000000
    return val

# ==========================================
# 1. AST Node & Parser
# ==========================================
class Node:
    def __init__(self, data, children):
        self.data = data
        self.children = children
    def __repr__(self):
        return f"Node({self.data}, {self.children})"

class MiniLispParser:
    def __init__(self):
        self.token_re = re.compile(
            r'(?P<ws>\s+)|'
            r'(?P<comment>//.*)|'
            r'(?P<lparen>\()|'
            r'(?P<rparen>\))|'
            r'(?P<bool>#t|#f)|'
            r'(?P<number>-?\d+)|'
            r'(?P<id>[a-z][a-z0-9-]*)'
            r'|(?P<op>[\+\-\*/><=]|\bmod\b)'
        )
        self.keyword_map = {
            'print-num': 'print_num', 'print-bool': 'print_bool',
            '+': 'plus', '-': 'minus', '*': 'multiply', '/': 'divide',
            'mod': 'modulus', '>': 'greater', '<': 'smaller', '=': 'equal',
            'and': 'and_op', 'or': 'or_op', 'not': 'not_op',
            'define': 'def_stmt', 'if': 'if_exp', 'fun': 'fun_exp'
        }

    def tokenize(self, text):
        pos = 0
        tokens = []
        while pos < len(text):
            match = self.token_re.match(text, pos)
            if not match: 
                raise SyntaxError(f"Illegal char at {pos}: '{text[pos]}'")
            kind = match.lastgroup
            val = match.group(kind)
            if kind == 'ws' or kind == 'comment': pass
            elif kind == 'number': tokens.append(('NUMBER', int(val)))
            elif kind == 'bool': tokens.append(('BOOL_VAL', val))
            elif kind == 'lparen': tokens.append(('LPAREN', '('))
            elif kind == 'rparen': tokens.append(('RPAREN', ')'))
            elif kind == 'id' or kind == 'op': tokens.append(('ID', val))
            pos = match.end()
        return tokens

    def parse(self, text):
        tokens = self.tokenize(text)
        if not tokens: return Node('program', [])
        stmts = []
        idx = 0
        while idx < len(tokens):
            node, next_idx = self._parse_stmt(tokens, idx)
            stmts.append(node)
            idx = next_idx
        return Node('program', stmts)

    def _parse_stmt(self, tokens, idx):
        if idx >= len(tokens): raise SyntaxError("Unexpected EOF")
        token_type, token_val = tokens[idx]
        if token_type in ('NUMBER', 'BOOL_VAL', 'ID'):
            return token_val, idx + 1
        elif token_type == 'LPAREN':
            return self._parse_sexpr(tokens, idx)
        else:
            raise SyntaxError(f"Unexpected token: {token_val}")

    def _parse_sexpr(self, tokens, idx):
        current = idx + 1
        if current >= len(tokens): raise SyntaxError("Unexpected EOF")
        head_type, head_val = tokens[current]
        
        if head_type == 'RPAREN': raise SyntaxError("Unexpected empty list")

        node_data = self.keyword_map.get(head_val)
        if node_data:
            current += 1
            children = []
            
            if node_data == 'fun_exp':
                if tokens[current][0] != 'LPAREN': raise SyntaxError("Fun needs args")
                fun_ids, next_idx = self._parse_fun_ids(tokens, current)
                children.append(fun_ids)
                current = next_idx
                body = []
                while tokens[current][0] != 'RPAREN':
                    child, next_idx = self._parse_stmt(tokens, current)
                    body.append(child)
                    current = next_idx
                children.append(Node('fun_body', body))
            else:
                while tokens[current][0] != 'RPAREN':
                    child, next_idx = self._parse_stmt(tokens, current)
                    children.append(child)
                    current = next_idx
            
            if tokens[current][0] != 'RPAREN': raise SyntaxError("Missing ')'")
            
            n = len(children)
            if node_data in ('plus', 'multiply', 'equal', 'and_op', 'or_op') and n < 2:
                raise SyntaxError(f"{head_val} expects >= 2 args")
            elif node_data in ('minus', 'divide', 'modulus', 'greater', 'smaller', 'def_stmt') and n != 2:
                raise SyntaxError(f"{head_val} expects 2 args")
            elif node_data in ('not_op', 'print_num', 'print_bool') and n != 1:
                raise SyntaxError(f"{head_val} expects 1 arg")
            elif node_data == 'if_exp' and n != 3:
                raise SyntaxError("if expects 3 args")

            return Node(node_data, children), current + 1
        else:
            children = []
            while tokens[current][0] != 'RPAREN':
                child, next_idx = self._parse_stmt(tokens, current)
                children.append(child)
                current = next_idx
            return Node('fun_call', children), current + 1

    def _parse_fun_ids(self, tokens, idx):
        current = idx + 1
        ids = []
        while tokens[current][0] != 'RPAREN':
            ids.append(tokens[current][1])
            current += 1
        return Node('fun_ids', ids), current + 1

# ==========================================
# 2. Interpreter Logic (修改運算部分)
# ==========================================
class Table(dict):
    def __init__(self, basic=False, names=None, values=None, outer=None):
        super().__init__()
        if names: self.update(zip(names, values))
        self.outer = outer
        if basic:
            self.update({
                'print_num': self.print_num, 'print_bool': self.print_bool,
                
                # --- 修改：所有數值運算都加上 to_int32() ---
                'plus': lambda *a: self.check(int, a) or to_int32(sum(a)),
                'minus': lambda *a: self.check(int, a) or to_int32(a[0]-a[1]),
                'multiply': lambda *a: self.check(int, a) or to_int32(reduce(lambda x,y: x*y, a)),
                'divide': lambda *a: self.check(int, a) or to_int32(int(a[0]/a[1])), # 使用 int(/) 模擬 C 行為
                'modulus': lambda *a: self.check(int, a) or to_int32(a[0]%a[1]),
                
                'greater': lambda *a: self.check(int, a) or a[0]>a[1],
                'smaller': lambda *a: self.check(int, a) or a[0]<a[1],
                'equal': lambda *a: self.check(int, a) or a.count(a[0])==len(a),
                'and_op': lambda *a: self.check(bool, a) or all(a),
                'or_op': lambda *a: self.check(bool, a) or any(a),
                'not_op': lambda a: self.check(bool, [a]) or not a
            })
            
    def check(self, t, a):
        for x in a: 
            if type(x)!=t: raise TypeError(f"Expect {t} got {type(x)}")
    def print_num(self, *a): self.check(int, a); print(a[0])
    def print_bool(self, *a): self.check(bool, a); print('#t' if a[0] else '#f')
    def find(self, n):
        if n in self: return self
        if self.outer: return self.outer.find(n)
        raise NameError(f"Var {n} not found")

class Function:
    def __init__(self, args, body, env):
        self.args = args
        self.body = body
        self.env = env
    def __call__(self, *p):
        return interpret_AST(self.body, Table(names=self.args, values=p, outer=self.env))

def interpret_AST(node, env=None):
    if env is None: env = Table(basic=True)
    if isinstance(node, int): return node # 這裡是 literal，parser 讀進來通常不會溢位，除非字面值就超大
    if node == '#t': return True
    if node == '#f': return False
    if isinstance(node, str): return env.find(node)[node]
    
    if node.data == 'program': 
        return [interpret_AST(c, env) for c in node.children]
    
    if node.data == 'fun_exp':
        args = interpret_AST(node.children[0], env)
        body_node = node.children[1] 
        return Function(args, body_node, env)

    if node.data == 'fun_call':
        func = interpret_AST(node.children[0], env)
        params = [interpret_AST(x, env) for x in node.children[1:]]
        return func(*params)
    
    if node.data == 'fun_ids': return node.children
    
    if node.data == 'fun_body':
        for s in node.children[:-1]: interpret_AST(s, env)
        return interpret_AST(node.children[-1], env)
        
    if node.data == 'def_stmt':
        env[node.children[0]] = interpret_AST(node.children[1], env)
        return
        
    if node.data == 'if_exp':
        test = interpret_AST(node.children[0], env)
        if type(test) != bool: raise TypeError("If expects bool")
        return interpret_AST(node.children[1 if test else 2], env)
    
    func = env.find(node.data)[node.data]
    args = [interpret_AST(x, env) for x in node.children]
    return func(*args)

if __name__ == '__main__':
    try:
        input_code = sys.stdin.read()
        parser = MiniLispParser()
        tree = parser.parse(input_code)
        interpret_AST(tree)
    except SyntaxError:
        print('syntax error')
    except TypeError:
        print('Type error!')
    except Exception:
        print('syntax error')