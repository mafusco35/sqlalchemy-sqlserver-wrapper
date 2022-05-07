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
