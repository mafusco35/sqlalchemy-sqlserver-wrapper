import urllib
from .custom_exceptions import UnknownDatabaseDriverError, ConnectionStringParsingError


def generate_sql_connection_string(
    server: str, database: str, uid: str = None, pwd: str = None
) -> str:
    """Returns a connection string to a SQL database.

    Args:
        server (str): name of SQL server
        database (str): database on server
        uid (str, optional): user id for server. Defaults to None.
        pwd (str, optional): password for server. Defaults to None.

    Raises:
        ConnectionStringParsingError: Exception raised if pwd
            is passed without uid

    Returns:
        str: SQL server connection string to provided server + database
    """
    if pwd is None:
        if uid is None:
            return (
                r"DRIVER={SQL Server};"
                f"SERVER={server};"
                f"DATABASE={database};"
                r"UID=;Trusted_Connection=Yes"
            )
        return (
            r"DRIVER={SQL Server};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={uid};"
            r"Trusted_Connection=Yes"
        )
    if uid is None:
        raise ConnectionStringParsingError()

    return (
        r"DRIVER={SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd}"
    )


def generate_sql_connection(
    server: str,
    database: str,
    uid: str = None,
    pwd: str = None,
    driver: str = "sqlalchemy",
) -> object:
    """Generate and return a connection object to a given SQL server and database

    Args:
        server (str): name of SQL server
        database (str): name of database on SQL server
        uid (str, optional): user id for server. Defaults to None.
        pwd (str, optional): password for server. Defaults to None.
            - NOTE: cannot give password without uid. Will throw an exception.
        driver (str, optional): Database connection driver. Defaults to 'sqlalchemy'
            - OPTIONS: sqlalchemy, pyodbc, pymssql

    Raises:
        ImportError: Unable to import specified SQL connection driver
        UnknownDatabaseDriverError: Unknown driver string.

    Returns:
        object: database connection object. Type depends on the driver string passed
        to the function
    """
    connection_string = generate_sql_connection_string(
        server, database, uid=uid, pwd=pwd
    )
    if driver == "sqlalchemy":
        try:
            from sqlalchemy import create_engine
        except ImportError:
            raise ImportError("Must have sqlalchemy installed to use sqlalchemy driver")

        return create_engine(
            f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"
        )

    elif driver == "pyodbc":
        try:
            import pyodbc
        except ImportError:
            raise ImportError("Must have pyodbc installed to use pyodbc driver")

        return pyodbc.connect(connection_string)

    elif driver == "pymssql":
        try:
            import pymssql
        except ImportError:
            raise ImportError("Must have pymssql installed to use pymssql driver")
        if uid is None or pwd is None:
            return pymssql.connect(server=server, database=database)
        return pymssql.connect(server=server, database=database, user=uid, password=pwd)

    else:
        raise UnknownDatabaseDriverError(
            f"""Unknown database connection driver: {driver}
            Options are: sqlalchemy, pyodbc, pymssql"""
        )
