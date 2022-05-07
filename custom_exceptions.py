class UnknownDatabaseDriverError(Exception):
    pass


class ConnectionStringParsingError(Exception):
    pass


class MissingSchemaError(Exception):
    pass


class MissingViewError(Exception):
    pass


class MissingTableError(Exception):
    pass
