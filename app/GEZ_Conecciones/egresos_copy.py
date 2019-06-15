import pyodbc

def read_db():
    con = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=gez_pruebas;uid=gezsa001;pwd=gez9105ru2")
    cur = con.cursor()
    
    return cur
    

sql = "SELECT * FROM dbo.docum_recepcion WHERE rcep_numero=42515"
cur = read_db()
cur.execute(sql)

for row in cur:
    print(row.colnumero,row.coldescripcion)

print('test succesfful')