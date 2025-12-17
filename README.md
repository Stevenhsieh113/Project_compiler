# Mini-LISP Interpreter

這是一個使用純 Python 實作的 Mini-LISP 語言直譯器。本專案不依賴任何第三方語法分析套件（如 `lark-parser`），而是包含了一個手寫的遞歸下降解析器（Recursive Descent Parser），能夠讀取、解析並執行 Mini-LISP 程式碼。

## 功能特色 (Features)

[cite_start]本直譯器支援 Mini-LISP 的核心語法與功能 [cite: 2, 3, 10]：

* **基本型別**：
    * [cite_start]**整數 (Integers)**: 支援有號整數運算。根據規格書定義，超出 $2^{31}-1$ 範圍的行為未定義，本實作採用 Python 的任意精度整數處理 [cite: 13]。
    * [cite_start]**布林值 (Booleans)**: `#t` (True) 與 `#f` (False) [cite: 12]。
* [cite_start]**數值運算**: `+`, `-`, `*`, `/`, `mod`, `>`, `<`, `=` [cite: 17]。
* [cite_start]**邏輯運算**: `and`, `or`, `not` [cite: 18]。
* [cite_start]**流程控制**: `if` 表達式 [cite: 183]。
* [cite_start]**變數定義**: `define` 語句 [cite: 151]。
* [cite_start]**函式功能** [cite: 159, 160]：
    * 支援匿名函式 `fun` (Lambda)。
    * 支援遞歸呼叫 (Recursion)。
    * 支援閉包 (Closure) 與巢狀函式定義。
    * 支援一級函式 (First-class functions)。
* **錯誤處理**:
    * **Syntax Error**: 針對語法結構錯誤或參數數量不正確，輸出 `syntax error`。
    * [cite_start]**Type Error**: 針對型別錯誤（如將布林值用於數值運算），輸出 `Type error!` 。

## 系統需求 (Requirements)

* Python 3.6 或以上版本。
* [cite_start]**無外部依賴**：不需要安裝 `lark` 或其他第三方套件 [cite: 1]（已移除原始需求的依賴）。

## 安裝與執行 (Usage)

### 1. 準備程式碼
確保目錄中包含主程式檔案（例如 `main.py`）。

### 2. 執行方式
直譯器讀取標準輸入 (Standard Input, stdin) 的內容進行執行。

#### 方式：互動式輸入 (Interactive)
在終端機直接執行 Python 腳本，cd進入該檔案資料夾，並輸入python main.py < xxxx.lsp。

```bash
python main.py

# Lexer

## 功能說明
將長字串切割成一個一個 Token。  
若出現未定義的特殊符號，Lexer 將無法匹配並回報錯誤。

---

## Token Regular Expression

```python
self.token_re = re.compile(
    r'(?P<ws>\s+)|'                  # 忽略空白
    r'(?P<comment>//.*)|'            # 忽略註解 (// 開頭)
    r'(?P<lparen>\()|'               # 左括號
    r'(?P<rparen>\))|'               # 右括號
    r'(?P<bool>#t|#f)|'              # 布林值 (#t, #f)
    r'(?P<number>-?\d+)|'            # 整數 (支援負數)
    r'(?P<id>[a-z][a-z0-9-]*)|'      # 識別字 (ID)
    r'|(?P<op>[\+\-\*/><=]|\bmod\b)' # 運算子
)
```

---

## Keyword Map

```python
self.keyword_map = {
    # I/O
    'print-num': 'print_num',
    'print-bool': 'print_bool',

    # 數學運算
    '+': 'plus',
    '-': 'minus',
    '*': 'multiply',
    '/': 'divide',
    'mod': 'modulus',
    '>': 'greater',
    '<': 'smaller',
    '=': 'equal',

    # 邏輯運算
    'and': 'and_op',
    'or': 'or_op',
    'not': 'not_op',

    # 核心語法
    'define': 'def_stmt',
    'if': 'if_exp',
    'fun': 'fun_exp'
}
```

---

## Token 類型

| Token | 說明 |
|------|------|
| ws | 空白（忽略） |
| comment | 註解（忽略） |
| lparen | `(` |
| rparen | `)` |
| bool | `#t`, `#f` |
| number | 整數 |
| id | 識別字 |
| op | 運算子 |

---

## 設計重點

- 空白與註解在 Lexer 階段即被忽略
- 非法字元無法被 token 化
- Keyword 與 identifier 分離，利於 Parser 設計



## Program
* Parser (parse 方法)： parse 函式中的 while idx < len(tokens): 迴圈負責處理這個 STMT+ 的定義。它會不斷呼叫 _parse_stmt 直到所有 Token 被讀取完畢，並將所有語句存入一個 Node('program', stmts) 節點。
* Interpreter (interpret_AST 函式)： 當遇到 node.data == 'program' 時，程式碼使用列表推導式 [interpret_AST(c, env) for c in node.children] 依序執行每一個語句。

## Print 
主要分為印出數字和印出#t和#f
* Parser: 定義'print-num': 'print_num' 和 'print-bool': 'print_bool'，在parser會先檢查是否有這兩個
* Interpreter: self.check(int, a)確保型別正確，然後輸出答案

## Expression(EXP)
包含了布林值、數字、變數，或是運算子、函式呼叫、IF 表達式
* Parser(_parse_stmt) : 判斷基礎型別(NUMBER, BOOL, ID)或是左括號，如果是左括號則進入複合表達式。
* Interpreter:
  (1) if isinstance(node, int): 專門處理數字
  (2) if node =='#t'/ '#f': 處理布林值
  (3) if isinstance(node, str): 處理變數
## NUM_OP
基本運算: 包含加減乘除, mod，且允許多參數
* Parser: 檢查是否符合至少兩個參數，有的話才能計算
* Interpreter:
  //注意!!: 因為題目規定數字範圍是signed integer: -2^31到2^31 -1，所以要加入to_int32()來設計
  Plus(+): 使用sum(a)來支援多參數相加
  Minus(-):
  Multiply: 使用reduce來支援多參數連成


### 1. Syntax Valid
輸入格式不符合預期輸入格式，將會輸出"syntax error的字樣，像是( + )這種少了相加的數字就會報syntax error。

### 2. 
