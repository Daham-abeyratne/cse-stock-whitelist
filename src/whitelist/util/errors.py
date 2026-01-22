class CSEWhitelistError(Exception):
    pass

class ConfigError(CSEWhitelistError):
    pass

class FetchError(CSEWhitelistError):
    pass

class StorageError(CSEWhitelistError):
    pass
