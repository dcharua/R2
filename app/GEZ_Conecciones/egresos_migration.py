import pyodbc
import pandas as pd


def read_db():
    con = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=gez_pruebas;uid=gezsa001;pwd=gez9105ru2")
    cur = con.cursor()
    
    return cur,con
    

#sql = "SELECT * FROM dbo.docum_recepcion WHERE rcep_numero=42515"


sql = "SELECT * FROM dbo.CuentasxPagar WHERE 1=0"
sql = "SELECT * FROM dbo.CuentasxPagar WHERE cxp_monto > 700000"
sql = "SELECT * FROM dbo.CuentasxPagar WHERE cxp_FECHA > '2013'"

cur,con = read_db()
data = pd.read_sql(sql,con)


data.to_csv('test_data.csv',index = False)
print(data.head())
data = pd.read_csv('test_data.csv')
print(data.head())

print('test succesfful')