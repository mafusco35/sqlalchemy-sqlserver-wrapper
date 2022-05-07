# sqlalchemy-sqlserver-wrapper
Thin wrapper for sqlalchemy aimed at SQL Server

connection_functions contains wrapper functions to return SQL server connection engines to a supplied server and database pair using the desired
python framework: sqlalchemy, pyodbc, or pymssql

if you choose to use sqlalchemy as your db connection library, then you can take advantage of the DatabaseConfig class

DatabaseConfig is contained in database_object_configuration.py and attempts to provide a thin wrapper for some sqlalchemy features. Each class
instance contains its own server/database connection and allows the user to specify which tables or views should be reflected into
sqlalchemy table objects. These objects are set as attributes to the DatabaseConfig class instance, and these tables are then available
for the typical sqlalchemy functionality

NOTE: the sqlalchemy table objects are setup to use sqlalchemy expression language (or core, NOT the ORM). There is currently no way to
switch to ORM behavior (at least, I don't think there is), though this could be added

Getting Started:

It is simple to use: if you just want a SQL server connection engine, call generate_sql_connection with your desired server and database names. You can also pass uid and pwd as optional keyword arguments. If uid and pwd are not provided, the server connection will be made using default Windows Authentication.

If you want to take advantage of the configuration class, simply call DatabaseConfig, again with server, database, and optional credentials, to instantiate the connection class. The engine attribute will be set for you (self.engine).

Then, call set_view or set_table to reflect a view/table from the database to a sqlalchemy core table object. You can specify the attribute name of the table that will be set to the class, otherwise it will default to the view/table name. There are also other methods that allow you to list all views, tables, or schema associated with self.engine. Support is also provided for different schema.
