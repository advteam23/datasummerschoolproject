#import numpy as np
import pandas as pd
import smtplib      #for sending function
import xlsxwriter
from google.cloud import bigquery
from datetime import date, timedelta
import email
import os
from email.mime.text import MIMEText
import datetime
import tkinter
from pandas import ExcelWriter
from tkinter import messagebox
from tkinter import *

from cleancode.functions import extract_data_fromBQ, send_email

def count_digits(number):
    Count = 0
    while (number > 0):
        number = number // 10
        Count = Count + 1
    return Count

def getInput():
    a = nome_prodotto.get()
    b = budget.get()
    c = anno_inizio.get()
    d = mese_inizio.get()
    e = giorno_inizio.get()
    f = durata_campagna.get()
    global params
    global closed
    params[0] = a   #prodotto
    params[1] = b   #budget
    params[2] = c   #anno
    params[3] = d   #mese
    params[4] = e   #giorno
    params[5] = f   #durata campagna
    tutto_ok = True
    if params[0] not in lista_prodotti:
        tutto_ok = False
        params = ['', 0, 0, 0, 0, 0]
        messagebox.showinfo("WARNING", "Inserire un prodotto valido")
    try:
        params[1] = float(params[1])
    except:
        params = ['', 0, 0, 0, 0, 0]
        tutto_ok = False
        messagebox.showinfo("WARNING", "Puoi inserire solo numeri nel campo del budget")
    try:
        params[2] = int(params[2])
    except:
        params = ['', 0, 0, 0, 0, 0]
        tutto_ok = False
        messagebox.showinfo("WARNING", "Puoi inserire solo numeri interi nel campo anno corrente")
    try:
        params[3] = int(params[3])
    except:
        params = ['', 0, 0, 0, 0, 0]
        tutto_ok = False
        messagebox.showinfo("WARNING", "Puoi inserire solo numeri interi nel campo mese corrente")
    try:
        params[4] = int(params[4])
    except:
        params = ['', 0, 0, 0, 0, 0]
        tutto_ok = False
        messagebox.showinfo("WARNING", "Puoi inserire solo numeri interi nel campo giorno corrente")
    try:
        params[5] = int(params[5])
    except:
        params = ['', 0, 0, 0, 0, 0]
        tutto_ok = False
        messagebox.showinfo("WARNING", "Puoi inserire solo numeri interi nel campo durata della campagna")
    if params[4] > 31 or params[4] < 1:
        tutto_ok = False
        params = ['', 0, 0, 0, 0, 0]
        messagebox.showinfo("WARNING", "Inserire un giorno valido")
    elif params[3] > 12 or params[3] < 1:
        tutto_ok = False
        params = ['', 0, 0, 0, 0, 0]
        messagebox.showinfo("WARNING", "Inserire un mese valido")
    count = count_digits(params[2])
    if count > 4 or params[2] < 0:
        tutto_ok = False
        params = ['', 0, 0, 0, 0, 0]
        messagebox.showinfo("WARNING", "Inserire un anno valido")
    if tutto_ok:
        closed = True   #It means that we can exit from the while because all the data are correct
    window.destroy()

def onClosing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        global closed
        closed = True
        window.destroy()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "resources/gcp_credentials.json"
print("Caricamento Database...")
data = extract_data_fromBQ()
print("Database caricato!")
#Scrittura del database su di un file
writer_1 = ExcelWriter('Database.xlsx')
data.to_excel(writer_1, sheet_name = 'Sheet1')
writer_1.close()

data.date = pd.to_datetime(data['date'], format = "%Y/%m/%d")
data['valuta'] = data['common_cost'].apply(lambda x: str(x))
data['valuta'] = data['valuta'].apply(lambda x: float(x.strip().replace(",",".")))
lista_prodotti = data.groupby('product').groups.keys()
group_by_date_min = data.groupby('product')['date'].min()
group_by_commoncost = data.groupby('product')['valuta'].sum()
pippo = data.groupby(['product', 'date'], as_index=False)['valuta'].sum()

closed = False

while True:
    if closed == True:
        break
    params = ['', 0, 0, 0, 0, 0]
    window = Tk()
    window.title("ADV")
    window.geometry('350x200')
    Label(window, text="Inserisci il nome del prodotto").grid(row=0, sticky = W)
    Label(window, text="Inserisci il budget").grid(row=1, sticky=W)
    Label(window, text="Inserisci anno corrente").grid(row=2, sticky=W)
    Label(window, text="Inserisci mese corrente").grid(row=3, sticky=W)
    Label(window, text="Inserisci giorno corrente").grid(row=4, sticky=W)
    Label(window, text="Inserisci durata campagna").grid(row=5, sticky=W)

    nome_prodotto = Entry(window)
    budget = Entry(window)
    anno_inizio = Entry(window)
    mese_inizio = Entry(window)
    giorno_inizio = Entry(window)
    durata_campagna = Entry(window)

    nome_prodotto.grid(row=0, column = 1)
    budget.grid(row=1, column = 1)
    anno_inizio.grid(row=2, column=1)
    mese_inizio.grid(row=3, column=1)
    giorno_inizio.grid(row=4, column=1)
    durata_campagna.grid(row=5, column=1)

    btn = Button(window, text = 'submit', command = getInput).grid(row=6, sticky=W)
    window.protocol("WM_DELETE_WINDOW", onClosing)
    window.mainloop()
if params[0]=='' or params[1]==0 or params[2]==0 or params[3]==0 or params[4]==0 or params[5]==0:
    exit(0)
nome_prodotto = params[0]
budget = float(params[1])
anno = int(params[2])
mese = int(params[3])
giorno = int(params[4])
durata_campagna = int(params[5])

data_inizio = group_by_date_min.loc[nome_prodotto]

data_attuale = datetime.datetime(anno, mese, giorno, 0, 0, 0)
difference = data_attuale-data_inizio
print("Giorni trascorsi: ", difference.days)

commonCost_product = group_by_commoncost.loc[nome_prodotto]
budget_giorn_teorico = budget/durata_campagna

print("Il tuo budget teorico è: ", budget_giorn_teorico)
print("Common cost totale del prodotto: ", commonCost_product)

idx=(pippo["product"]==nome_prodotto) & (pippo["date"]>=data_inizio) & (pippo["date"]<data_attuale)
commonCost_ad_oggi = pippo.loc[idx, 'valuta'].sum()
print("CommonCost ad oggi: ", commonCost_ad_oggi)

budget_teorico_oggi = budget_giorn_teorico*(difference.days)
print("Budget teorico oggi: ", budget_teorico_oggi)

situazione_attuale = commonCost_ad_oggi - budget_teorico_oggi
print("Situazione attuale: ", situazione_attuale)
if situazione_attuale == 0:
    print("Perfetto")

elif situazione_attuale > 0:
    print("OVERSPENDING!! ")
    giorni_rimasti = durata_campagna-difference.days
    budget_rimanente = budget-commonCost_ad_oggi
    body = 'Devi spendere ' + str(budget_rimanente/giorni_rimasti) + ' ogni giorno, per ' + str(giorni_rimasti) + ' giorni'
    print(body)
    subject = "Overspending Alert"
    from_addr = "advteam23@gmail.com"
    pwd = "FFTal23."
    #definizione di una finestra per immettere l'indirizzo
    f = open("destinatari.txt")
    destinatari = f.readlines()
    print("Indirizzi dei destinatari: ", destinatari)
    for el in destinatari:
        to_addr = el
        send_email(from_addr, pwd, to_addr, subject, body)
else:
    x = situazione_attuale*100/(budget_teorico_oggi*0.9)
    print("Percentuale: ", -x, "%")
    if -x < 10:

        print("Perfetto: No Underspending")
    else:
        print("UNDERSPENDING!")
        giorni_rimasti = durata_campagna - difference.days
        budget_rimanente = budget - commonCost_ad_oggi
        body = "Devi spendere " + str(budget_rimanente / giorni_rimasti) + " ogni giorno, per " + str(giorni_rimasti) + " giorni"
        subject = "Underspending Alert"
        from_addr = "advteam23@gmail.com"
        pwd = "FFTal23."
        f = open("destinatari.txt")
        destinatari = f.readlines()
        print("Indirizzi dei destinatari: ", destinatari)
        for el in destinatari:
            to_addr = el
            send_email(from_addr, pwd, to_addr, subject, body)