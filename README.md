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

Lexer 設計說明

本專案的 Lexer（詞彙分析器） 負責將輸入的原始程式碼字串切割成一個一個的 Token，以便後續 Parser 進行語法分析。
若輸入中出現不符合語法規則的字元或符號，Lexer 將無法成功匹配並視為錯誤。

Token 規則（Regular Expressions）

Lexer 使用 Python 的 re 模組，透過以下正則表達式定義各類 Token：

self.token_re = re.compile(
    r'(?P<ws>\s+)|'                  # 空白字元（忽略）
    r'(?P<comment>//.*)|'            # 註解（// 開頭，忽略）
    r'(?P<lparen>\()|'               # 左括號 '('
    r'(?P<rparen>\))|'               # 右括號 ')'
    r'(?P<bool>#t|#f)|'              # 布林值 (#t, #f)
    r'(?P<number>-?\d+)|'            # 整數（支援負數）
    r'(?P<id>[a-z][a-z0-9-]*)|'      # 識別字（identifier）
    r'(?P<op>[\+\-\*/><=]|\bmod\b)'  # 運算子
)

Token 類型說明
Token 類型	說明
ws	空白字元（會被忽略）
comment	註解（// 開頭，會被忽略）
lparen	左括號 (
rparen	右括號 )
bool	布林常數 #t、#f
number	整數（包含負數）
id	識別字（小寫字母開頭，可包含數字與 -）
op	運算子（+ - * / > < = mod）
關鍵字對應表（Keyword Map）

Lexer 會先將字串辨識為 id 或 op，再透過 keyword_map 將其轉換為對應的語法 Token 類型。

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

關鍵字分類

I/O 指令：print-num, print-bool

數學運算子：+, -, *, /, mod

比較運算子：>, <, =

邏輯運算：and, or, not

核心語法結構：define, if, fun
### 1. Syntax Valid
輸入格式不符合預期輸入格式，將會輸出"syntax error的字樣，像是( + )這種少了相加的數字就會報syntax error。

### 2. 
