#import numpy as np
import pandas as pd
import smtplib      #for sending function
import xlsxwriter
from google.cloud import bigquery
from datetime import date, timedelta
import os
from email.message import EmailMessage
import datetime
import tkinter
from pandas import ExcelWriter
from tkinter import messagebox
from tkinter import *

from cleancode.functions import extract_data_fromBQ

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "resources/gcp_credentials.json"

data = extract_data_fromBQ()
data.date = pd.to_datetime(data['date'], format = "%Y/%m/%d")
data['valuta'] = data['common_cost'].apply(lambda x: str(x))
data['valuta'] = data['valuta'].apply(lambda x: float(x.strip().replace(",",".")))
data['clicks'] = data['common_clicks'].apply(lambda x: float(x) if x != None else 0)
data['impressions'] = data['common_impressions'].apply(lambda x: float(x) if x != None else 0)
data['conversions'] = data['conversions'].apply(lambda x: float(x) if x != None else 0)
pluto = data.groupby(['product', 'sourceType', 'campaign_name']).agg({"valuta":"sum",
                                                                                       "clicks":"sum",
                                                                                       "impressions":"sum",
                                                                                       "conversions":"sum"})

pluto['campoCalcolato1'] = pluto['valuta']/pluto['impressions']
pluto['campoCalcolato2'] = pluto['valuta']/pluto['clicks']
pluto['campoCalcolato3'] = pluto['valuta']/pluto['conversions']
pluto['campoCalcolato4'] = pluto['clicks']/pluto['impressions']*100
writer = ExcelWriter('Opzionale.xlsx')
pluto.to_excel(writer, sheet_name = 'Sheet1')
writer.close()
messagebox.showinfo("ADV", "Dataframe succesfully written on Excel file 'Opzionale.xlsx'")