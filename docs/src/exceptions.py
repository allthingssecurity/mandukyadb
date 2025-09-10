class MandukyaError(Exception):
    """Base exception for MandukyaDB"""
    pass

class ParseError(MandukyaError):
    """Error parsing SQL statement"""
    pass

class ExecutionError(MandukyaError):
    """Error executing SQL statement"""
    pass

class StorageError(MandukyaError):
    """Error in storage engine"""
    pass

