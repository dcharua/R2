#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 23:54:17 2019

@author: abazbaz
"""

import pyodbc
import pandas as pd

def connect_to_db(sql):
    con=pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};server=dodder.arvixe.com;database=gez_pruebas;uid=gezsa001;pwd=gez9105ru2")   
    data = pd.read_sql(sql, con)    
    
    return data