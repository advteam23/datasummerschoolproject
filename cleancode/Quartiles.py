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

from cleancode.functions import extract_data_fromBQ, send_email

def getInput():
    a = prodotto.get()
    b = campagna.get()
    global tupla
    global closed
    tupla = (a,b)
    tutto_ok = True
    if tupla not in lista:
        tutto_ok = False
        tupla = ('','')
        messagebox.showinfo("WARNING", "Inserire una coppia prodotto-campagna valida")
    if tutto_ok:
        closed = True   #It means that we can exit from the while because all the data are correct
    window.destroy()

def quantile_calculation_1(a):
    return a.quantile([0.25]).values[0]
def quantile_calculation_2(a):
    return a.quantile([0.75]).values[0]

def onClosing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        global closed
        closed = True
        window.destroy()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "resources/gcp_credentials.json"

data = extract_data_fromBQ()
data.date = pd.to_datetime(data['date'], format = "%Y/%m/%d")
data['valuta'] = data['common_cost'].apply(lambda x: str(x))
data['valuta'] = data['valuta'].apply(lambda x: float(x.strip().replace(",",".")))
lista_prodotti = data.groupby('product').groups.keys()
data['clicks'] = data['common_clicks'].apply(lambda x: float(x) if x != None else 0)
data['impressions'] = data['common_impressions'].apply(lambda x: float(x) if x != None else 0)
data['conversions'] = data['conversions'].apply(lambda x: float(x) if x != None else 0)

topolino = data.groupby(['product', 'campaign_name', 'date'], as_index = False).agg({"clicks":"sum",
                                                                                            "impressions" : "sum"})
topolino['campoCalcolato4'] = topolino['clicks']/topolino['impressions']*100

y = topolino.groupby(['campaign_name'], as_index = False).agg({"campoCalcolato4":quantile_calculation_1})
z = topolino.groupby(['campaign_name'], as_index = False).agg({"campoCalcolato4":quantile_calculation_2})
res = pd.merge(topolino, y, on='campaign_name', how = 'left')
complete = pd.merge(res, z, on='campaign_name', how = 'left')
complete.rename(columns={'product': 'product', 'campaign_name': 'campaign_name', 'date':'date', 'clicks':'clicks', 'impressions':'impressions', 'campoCalcolato4_x':'CTR', 'campoCalcolato4_y':'primo_quartile', 'campoCalcolato4':'terzo_quartile'}, inplace=True)
writer = ExcelWriter('Quartili.xlsx')
complete.to_excel(writer, sheet_name = 'Sheet1')
writer.close()

lista = complete.groupby(['product', 'campaign_name']).groups.keys()
prodotto = ''
campaign = ''
closed = False
while True:
    if closed == True:
        break
    tupla = ('','')
    window = Tk()
    window.title("ADV")
    window.geometry('350x200')
    Label(window, text="Inserisci il nome del prodotto").grid(row=0, sticky = W)
    Label(window, text="Inserisci il nome della campagna").grid(row=1, sticky=W)

    prodotto = Entry(window)
    campagna = Entry(window)

    prodotto.grid(row=0, column = 1)
    campagna.grid(row=1, column=1)

    btn = Button(window, text = 'submit', command = getInput).grid(row=6, sticky=W)
    window.protocol("WM_DELETE_WINDOW", onClosing)
    window.mainloop()
prodotto = tupla[0]
campaign = tupla[1]
subset = complete[complete['product']==prodotto]
subset_2 = subset[subset['campaign_name']==campaign]
subset_3 = subset_2.groupby(['product', 'campaign_name'], as_index=False)['date'].max()
data_max = subset_3.iloc[0]['date']

subset_4 = subset_2[subset['date']==data_max]
valore = subset_4.iloc[0]['CTR']
quartile_25 = subset_4.iloc[0]['primo_quartile']
quartile_75 = subset_4.iloc[0]['terzo_quartile']
print("CTR: ", valore)
print("Primo quartile: ", quartile_25)
print("Terzo quartile: ", quartile_75)
if valore > quartile_75:
    print("Fantastico!")
elif valore < quartile_25:
    from_addr = "advteam23@gmail.com"
    pwd = "FFTal23."
    subject = "Alert !!"
    body = "Il CTR è minore del primo quartile!"
    f = open("destinatari.txt")
    destinatari = f.readlines()
    print("Indirizzi dei destinatari: ", destinatari)
    for el in destinatari:
        to_addr = el
        send_email(from_addr, pwd, to_addr, subject, body)
else:
    from_addr = "advteam23@gmail.com"
    pwd = "FFTal23."
    subject = "Alert !!"
    body = "Va bene, ma potresti fare di meglio!"
    f = open("destinatari.txt")
    destinatari = f.readlines()
    print("Indirizzi dei destinatari: ", destinatari)
    for el in destinatari:
        to_addr = el
        send_email(from_addr, pwd, to_addr, subject, body)
