import pyodbc
import pandas as pd

# Create connection
con = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=gez_pruebas;uid=gezsa001;pwd=gez9105ru2")
   
    

def migrate_

#sql = "SELECT * FROM dbo.docum_recepcion WHERE rcep_numero=42515"


sql = "SELECT * FROM dbo.CuentasxPagar WHERE 1=0"
sql = "SELECT * FROM dbo.CuentasxPagar WHERE cxp_monto > 700000"
sql = "SELECT * FROM dbo.CuentasxPagar WHERE cxp_FECHA > '2013'"



def migrate_egresos(con)
    sql = "SELECT * FROM dbo.CuentasxPagar WHERE cxp_FECHA > '2013'"
    data = pd.read_sql(sql,con)
    print(len(data))
    print(ldata.head())

    sql = "SELECT * FROM dbo.CuentasxPagar WHERE cxp_FECHA > '2013'"
    data = pd.read_sql(sql,con)
    print(len(data))
    print(ldata.head())



migrate_egresos(con)

print('test succesfful')