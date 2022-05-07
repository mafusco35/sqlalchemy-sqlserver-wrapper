import sqlalchemy

from .custom_exceptions import MissingSchemaError, MissingTableError, MissingViewError
from . import connection_functions


class DatabaseConfig:
    """sqlalchemy database configuration class.
    SQL connection engine will be created upon initialization.

    Tables / views of interest must be set to class instance individually.
    These can be set with one of two methods:
        - set_table(table, attr_name=None, schema='dbo')
        - set_view(view, attr_name=None, schema='dbo')

    Calling these methods will trigger the specified table or view
    to be 'reflected' into a sqlalchemy table object.

    The sqlalchemy table object will be set as an instance attribute
    according to the attr_name passed to set_table or set_view methods.
    """

    def __init__(self, server: str, database: str, uid: str = None, pwd: str = None):
        """Initialize class instance. Pass server + database connection credentials.

        NOTE: If uid and pwd are None, standard Windows authentication will be used

        Args:
            server (str): SQL server to connect to
            database (str): database in specified server
            uid (str, optional): user id used to log into server and database.
                - Defaults to None.
            pwd (str, optional): password used to log into server and database.
                - Defaults to None.
        """
        self.server = server
        self.database = database
        self.uid = uid
        self.pwd = pwd
        self.metadata_dict = {}
        self._create_engine()

    def set_table(self, table: str, attr_name: str = None, schema: str = "dbo"):
        """Call this method to reflect a table from the current database connection.
        If attr_name is not specified, the instance attribute will default to the table
        name. The specified view will be set as an instance attribute if the table
        exists for the given connection and schema. If not, an exception will be
        raised

        Args:
            table (str): name of SQL table to be reflected
            attr_name (str, optional): name of class instance attribute corresponding
                to the desired table. Defaults to None.
                - NOTE: default will be set to table name
            schema (str, optional): schema in which table resides. Defaults to "dbo".
                - NOTE: if you set two views with the same attr_name from two
                different schema, the latter will overwrite the former.
                It is up to the user to specify an appropriate attr_name
        """
        if attr_name is None:
            attr_name = table
        tbl = self._reflect_table(table, schema)
        setattr(self, attr_name, tbl)
        return

    def set_view(self, view: str, attr_name: str = None, schema: str = "dbo"):
        """Call this method to reflect a view from the current database connection.
        If attr_name is not specified, the instance attribute will default to the view
        name. The specified view will be set as an instance attribute if the view
        exists for the given connection and schema. If not, an exception will be
        raised

        Args:
            view (str): name of SQL view to be reflected
            attr_name (str, optional): name of class instance attribute corresponding
                to the desired view. Defaults to None.
                - NOTE: default will be set to view name
            schema (str, optional): schema in which view resides. Defaults to "dbo".
                - NOTE: if you set two views with the same attr_name from two
                different schema, the latter will overwrite the former.
                It is up to the user to specify an appropriate attr_name
        """
        if attr_name is None:
            attr_name = view
        vw = self._reflect_view(view, schema)
        setattr(self, attr_name, vw)
        return

    def _create_engine(self):
        """Call connection_functions.generate_sql_connection to create sqlalchemy engine
        Will raise exception for specifying pwd without uid
        """
        self.engine = connection_functions.generate_sql_connection(
            self.server, self.database, uid=self.uid, pwd=self.pwd, driver="sqlalchemy"
        )

    def _reflect_view(self, view: str, schema: str) -> sqlalchemy.Table:
        """Reflect view from connection engine.
        Checks for the existence of both schema and view
        within the database. Will raise exceptions if either
        cannot be located.

        Args:
            view (str): name of view to be reflected
            schema (str): schema name of view location

        Raises:
            MissingSchemaError: Exception if specified schema cannot be found
                in [SERVER].[DATABASE] connection
            MissingTableError: Exception if specified view cannot be found
                in [SERVER].[DATABASE].[SCHEMA] connection

        Returns:
            sqlalchemy.Table: sqlalchemy core table object
        """
        # Check for schema in database connection
        if schema not in self._list_schema_from_engine():
            raise MissingSchemaError(
                f"Schema: {schema} is missing from {self.server}.{self.database}"
            )
        # Add schema to metadata_dict
        if schema not in self.metadata_dict:
            self.metadata_dict[schema] = sqlalchemy.MetaData(schema=schema)
        # Check for view in database + schema
        if view not in self._list_views_from_engine(schema):
            raise MissingViewError(
                f"View: {view} is missing from {self.server}.{self.database}.{schema}"
            )
        return sqlalchemy.Table(
            view, self.metadata_dict[schema], autoload_with=self.engine
        )

    def _reflect_table(self, table: str, schema: str) -> sqlalchemy.Table:
        """Reflect table from connection engine.
        Checks for the existence of both schema and table
        within the database. Will raise exceptions if either
        cannot be located.

        Args:
            table (str): name of table to be reflected
            schema (str): schema name of table location

        Raises:
            MissingSchemaError: Exception if specified schema cannot be found
                in [SERVER].[DATABASE] connection
            MissingTableError: Exception if specified table cannot be found
                in [SERVER].[DATABASE].[SCHEMA] connection

        Returns:
            sqlalchemy.Table: sqlalchemy core table object
        """
        # Check for schema in database connection
        if schema not in self._list_schema_from_engine():
            raise MissingSchemaError(
                f"Schema: {schema} is missing from {self.server}.{self.database}"
            )
        # Add schema to metadata_dict
        if schema not in self.metadata_dict:
            self.metadata_dict[schema] = sqlalchemy.MetaData(schema=schema)
        # Check for table in database + schema
        if table not in self._list_tables_from_engine(schema):
            raise MissingTableError(
                f"View: {table} is missing from {self.server}.{self.database}.{schema}"
            )
        return sqlalchemy.Table(
            table, self.metadata_dict[schema], autoload_with=self.engine
        )

    def _list_views_from_engine(self, schema: str = None):
        """List views on connection with provided schema.
        If schema is None, views across all schema will be returned

        Args:
            schema (str, optional): Schema. Defaults to None.

        Returns:
            (type): list of views on current connection and schema
        """
        if schema is None:
            return sqlalchemy.inspect(self.engine).get_view_names()
        return sqlalchemy.inspect(self.engine).get_view_names(schema)

    def _list_tables_from_engine(self, schema: str = None):
        """List tables on connection with provided schema.
        If schema is None, tables across all schema will be returned

        Args:
            schema (str, optional): _description_. Defaults to None.

        Returns:
            _type_: list of tables on current connection and schema
        """
        if schema is None:
            return sqlalchemy.inspect(self.engine).get_table_names()
        return sqlalchemy.inspect(self.engine).get_table_names(schema)

    def _list_schema_from_engine(self):
        return sqlalchemy.inspect(self.engine).get_schema_names()

    def __str__(self):
        return f"""
        Connection for: {self.server}.{self.database}
        Current tables/views:
        {[{a: getattr(self, a).name}
        for a in dir(self)
        if isinstance(getattr(self,a), sqlalchemy.Table)]}
        """
