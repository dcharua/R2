




#####  
'''
Instructions to install on  Microsoft ODBC Driver for SQL Server on Linux

1. find Linux Distribution of your machine:
    'cat /etc/issue'

2. sudo su 
3. curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

4. #Download appropriate package for the OS version
   #Choose only ONE of the following, corresponding to your OS version

    #Ubuntu 14.04
    curl https://packages.microsoft.com/config/ubuntu/14.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

    #Ubuntu 16.04
    curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

    #Ubuntu 18.04
    curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

    #Ubuntu 18.10
    curl https://packages.microsoft.com/config/ubuntu/18.10/prod.list > /etc/apt/sources.list.d/mssql-release.list

5. exit
6. sudo apt-get update
7. sudo ACCEPT_EULA=Y apt-get install msodbcsql17

Now you can run the following function:
(run pip install pyodbc if needed)
'''
import pyodbc 

def read_db()
    con=pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com,1433;database=gez_pruebas;uid=gezsa001;pwd=gez9105ru2")
    cur=con.cursor()
    
    return cur
    

sql = "select * from colores where coldescripcion like '%NEGR%' ORDER BY COLNUMERO"
cur = sead_db()
cur.execute(sql)

for row in cur:
    print(row.colnumero,row.coldescripcion)

print('test succesfful')