"""
SQL Parser - Swapna (Dreaming State)
Handles abstract query parsing and planning
"""

import re
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from .exceptions import ParseError

@dataclass
class Column:
    name: str
    data_type: str
    constraints: List[str] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []

@dataclass
class CreateTableStatement:
    table_name: str
    columns: List[Column]

@dataclass
class InsertStatement:
    table_name: str
    columns: Optional[List[str]]
    values: List[Any]

@dataclass
class SelectStatement:
    columns: List[str]  # ['*'] for all columns
    table_name: str
    where_clause: Optional[Dict[str, Any]] = None
    order_by: Optional[List[str]] = None
    limit: Optional[int] = None

@dataclass
class DeleteStatement:
    table_name: str
    where_clause: Optional[Dict[str, Any]] = None

@dataclass
class DescribeStatement:
    table_name: str

class SQLParser:
    """SQL Parser implementing the Swapna (Dreaming) principle"""
    
    def __init__(self):
        self.keywords = {
            'CREATE', 'TABLE', 'INSERT', 'INTO', 'VALUES', 'SELECT', 
            'FROM', 'WHERE', 'DELETE', 'ORDER', 'BY', 'LIMIT',
            'DESCRIBE', 'DESC',  # Add DESCRIBE commands
            'INTEGER', 'TEXT', 'REAL', 'BLOB', 'NULL'
        }
    
    def parse(self, sql: str) -> Union[CreateTableStatement, InsertStatement, SelectStatement, DeleteStatement, DescribeStatement]:
        """Parse SQL statement into AST"""
        sql = sql.strip().rstrip(';')
        tokens = self._tokenize(sql)
        
        if not tokens:
            raise ParseError("Empty SQL statement")
        
        statement_type = tokens[0].upper()
        
        if statement_type == 'CREATE':
            return self._parse_create_table(tokens)
        elif statement_type == 'INSERT':
            return self._parse_insert(tokens)
        elif statement_type == 'SELECT':
            return self._parse_select(tokens)
        elif statement_type == 'DELETE':
            return self._parse_delete(tokens)
        elif statement_type in ['DESCRIBE', 'DESC']:
            return self._parse_describe(tokens)
        else:
            raise ParseError(f"Unsupported statement type: {statement_type}")
    
    def _tokenize(self, sql: str) -> List[str]:
        """Tokenize SQL string preserving delimiters used by the parser.

        Splits on whitespace but keeps parentheses and commas as individual tokens.
        Quotes around string literals are stripped so downstream parsing can
        treat them as a single token.
        """
        import re

        pattern = r'(\(|\)|,|;|\s+)'
        parts = re.split(pattern, sql)

        tokens: List[str] = []
        for part in parts:
            if part is None:
                continue
            part = part.strip()
            if not part:
                continue
            if part == ';':
                # statement terminator not needed by the AST
                continue
            # Handle quoted strings
            if part.startswith("'") and part.endswith("'") and len(part) >= 2:
                tokens.append(part[1:-1])
            else:
                tokens.append(part)

        return tokens
    
    def _parse_create_table(self, tokens: List[str]) -> CreateTableStatement:
        """Parse CREATE TABLE statement"""
        if len(tokens) < 4 or tokens[1].upper() != 'TABLE':
            raise ParseError("Invalid CREATE TABLE syntax")
        
        table_name = tokens[2]
        
        # Find column definitions between parentheses
        # Simplified parser - assumes format: CREATE TABLE name (col1 type1, col2 type2)
        try:
            # Find parentheses bounds
            paren_start = None
            paren_end = None
            for i, tok in enumerate(tokens):
                if tok == '(' and paren_start is None:
                    paren_start = i
                if tok == ')':
                    paren_end = i
            if paren_start is None or paren_end is None or paren_end <= paren_start:
                raise ParseError("Missing or invalid parentheses in CREATE TABLE")

            inner = tokens[paren_start + 1:paren_end]
            columns = self._parse_column_definitions(inner)

            return CreateTableStatement(table_name, columns)

        except Exception as e:
            raise ParseError(f"Error parsing CREATE TABLE: {e}")
    
    def _parse_column_definitions(self, tokens: List[str]) -> List[Column]:
        """Parse column definitions from tokens inside parentheses.

        Splits on commas and interprets: name TYPE [constraints...]
        """
        columns: List[Column] = []
        buf: List[str] = []

        def flush():
            nonlocal buf
            if not buf:
                return
            parts = buf
            if len(parts) < 2:
                buf = []
                return
            col_name = parts[0]
            col_type = parts[1].upper()
            constraints = parts[2:] if len(parts) > 2 else []
            columns.append(Column(col_name, col_type, constraints))
            buf = []

        for tok in tokens:
            if tok == ',':
                flush()
            else:
                buf.append(tok)
        flush()

        return columns
    
    def _parse_insert(self, tokens: List[str]) -> InsertStatement:
        """Parse INSERT statement"""
        if len(tokens) < 4 or tokens[1].upper() != 'INTO':
            raise ParseError("Invalid INSERT syntax")
        
        table_name = tokens[2]
        
        # Find VALUES keyword
        values_idx = None
        for i, token in enumerate(tokens):
            if token.upper() == 'VALUES':
                values_idx = i
                break
        
        if values_idx is None:
            raise ParseError("Missing VALUES in INSERT statement")
        
        # Extract values between parentheses and split by commas
        tail = tokens[values_idx + 1:]
        try:
            l = tail.index('(')
            r = len(tail) - 1 - tail[::-1].index(')')
            inner = tail[l + 1:r]
        except ValueError:
            inner = tail

        values: List[Any] = []
        buf: List[str] = []

        def push_value(parts: List[str]):
            if not parts:
                return
            token = ' '.join(parts)
            if token.isdigit():
                values.append(int(token))
            else:
                # float detection
                try:
                    if token.count('.') == 1 and all(p.isdigit() for p in token.split('.')):
                        values.append(float(token))
                    else:
                        values.append(token)
                except Exception:
                    values.append(token)

        for tok in inner:
            if tok == ',':
                push_value(buf)
                buf = []
            else:
                buf.append(tok)
        push_value(buf)
        
        return InsertStatement(table_name, None, values)
    
    def _parse_select(self, tokens: List[str]) -> SelectStatement:
        """Parse SELECT statement"""
        if len(tokens) < 3:
            raise ParseError("Invalid SELECT syntax")
        
        # Find FROM keyword
        from_idx = None
        for i, token in enumerate(tokens):
            if token.upper() == 'FROM':
                from_idx = i
                break
        
        if from_idx is None:
            raise ParseError("Missing FROM in SELECT statement")
        
        # Extract columns (split by commas)
        column_tokens = tokens[1:from_idx]
        if len(column_tokens) == 1 and column_tokens[0] == '*':
            columns = ['*']
        else:
            cols: List[str] = []
            buf: List[str] = []
            for tok in column_tokens:
                if tok == ',':
                    if buf:
                        cols.append(' '.join(buf))
                        buf = []
                else:
                    buf.append(tok)
            if buf:
                cols.append(' '.join(buf))
            columns = [c.strip() for c in cols if c.strip()]
        
        # Extract table name
        table_name = tokens[from_idx + 1]
        
        # Handle WHERE clause (simplified)
        where_clause = None
        where_idx = None
        for i, token in enumerate(tokens):
            if token.upper() == 'WHERE':
                where_idx = i
                break
        
        if where_idx is not None and where_idx + 3 < len(tokens):
            # Simple WHERE clause: column = value
            col = tokens[where_idx + 1]
            op = tokens[where_idx + 2]
            val = tokens[where_idx + 3]
            
            # Convert value
            if val.isdigit():
                val = int(val)
            elif val.replace('.', '').isdigit():
                val = float(val)
            
            where_clause = {'column': col, 'operator': op, 'value': val}
        
        return SelectStatement(columns, table_name, where_clause)
    
    def _parse_delete(self, tokens: List[str]) -> DeleteStatement:
        """Parse DELETE statement"""
        if len(tokens) < 3 or tokens[1].upper() != 'FROM':
            raise ParseError("Invalid DELETE syntax")
        
        table_name = tokens[2]
        
        # Handle WHERE clause (simplified)
        where_clause = None
        where_idx = None
        for i, token in enumerate(tokens):
            if token.upper() == 'WHERE':
                where_idx = i
                break
        
        if where_idx is not None and where_idx + 3 < len(tokens):
            col = tokens[where_idx + 1]
            op = tokens[where_idx + 2] 
            val = tokens[where_idx + 3]
            
            if val.isdigit():
                val = int(val)
            elif val.replace('.', '').isdigit():
                val = float(val)
            
            where_clause = {'column': col, 'operator': op, 'value': val}
        
        return DeleteStatement(table_name, where_clause)
    
    def _parse_describe(self, tokens: List[str]) -> DescribeStatement:
        """Parse DESCRIBE or DESC statement"""
        if len(tokens) < 2:
            raise ParseError("Invalid DESCRIBE syntax - missing table name")
        
        table_name = tokens[1]
        return DescribeStatement(table_name)
