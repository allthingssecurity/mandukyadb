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
        """Tokenize SQL string"""
        # Improved tokenizer that handles parentheses better
        import re
        
        # Split on whitespace but preserve parentheses and commas as separate tokens
        pattern = r'(\(|\)|,|;|\s+)'
        parts = re.split(pattern, sql)
        
        tokens = []
        for part in parts:
            part = part.strip()
            if part and part not in [',', ';']:
                # Handle quoted strings
                if part.startswith("'") and part.endswith("'"):
                    tokens.append(part[1:-1])  # Remove quotes
                elif part in ['(', ')']:
                    tokens.append(part)
                elif part:  # Skip empty strings and whitespace
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
            paren_start = None
            for i, token in enumerate(tokens):
                if '(' in token:
                    paren_start = i
                    break
            
            if paren_start is None:
                raise ParseError("Missing opening parenthesis in CREATE TABLE")
            
            # Extract column definitions
            column_tokens = tokens[paren_start:]
            columns = self._parse_column_definitions(column_tokens)
            
            return CreateTableStatement(table_name, columns)
            
        except Exception as e:
            raise ParseError(f"Error parsing CREATE TABLE: {e}")
    
    def _parse_column_definitions(self, tokens: List[str]) -> List[Column]:
        """Parse column definitions from tokens"""
        columns = []
        
        # Simple approach: join tokens and split by comma
        column_text = ' '.join(tokens)
        column_text = column_text.strip('()')
        
        for col_def in column_text.split(','):
            col_def = col_def.strip()
            parts = col_def.split()
            
            if len(parts) >= 2:
                col_name = parts[0]
                col_type = parts[1].upper()
                constraints = parts[2:] if len(parts) > 2 else []
                
                columns.append(Column(col_name, col_type, constraints))
        
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
        
        # Extract values
        values_tokens = tokens[values_idx + 1:]
        values_text = ' '.join(values_tokens).strip('()')
        
        values = []
        for value in values_text.split(','):
            value = value.strip()
            # Try to convert to appropriate type
            if value.isdigit():
                values.append(int(value))
            elif value.replace('.', '').isdigit():
                values.append(float(value))
            else:
                values.append(value)
        
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
        
        # Extract columns
        column_tokens = tokens[1:from_idx]
        if len(column_tokens) == 1 and column_tokens[0] == '*':
            columns = ['*']
        else:
            columns = [col.strip() for col in ' '.join(column_tokens).split(',')]
        
        # Extract table name
        table_name = tokens[from_idx + 1]
        
        # Handle WHERE clause (simplified)
        where_clause = None
        where_idx = None
        for i, token in enumerate(tokens):
            if token.upper() == 'WHERE':
                where_idx = i
                break
        
        if where_idx and where_idx + 3 < len(tokens):
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
        
        if where_idx and where_idx + 3 < len(tokens):
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