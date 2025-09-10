"""
Custom exceptions for MandukyaDB
"""

class MandukyaError(Exception):
    """Base exception for all MandukyaDB errors"""
    pass

class ParseError(MandukyaError):
    """Raised when SQL parsing fails"""
    pass

class ExecutionError(MandukyaError):
    """Raised when query execution fails"""
    pass

class StorageError(MandukyaError):
    """Raised when storage operations fail"""
    pass

class TransactionError(MandukyaError):
    """Raised when transaction operations fail"""
    pass