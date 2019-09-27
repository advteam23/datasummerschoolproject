import smtplib
import os
from email.mime.text import MIMEText

from google.cloud import bigquery

def extract_data_fromBQ():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "resources/gcp_credentials.json"
    client = bigquery.Client("summerschool-253810")
    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False
    query = ("SELECT * FROM `summerschool-253810.tag_school.all_data_from_each_channel`")
    query_job = client.query(query, job_config=job_config)
    result = query_job.result().to_dataframe()
    return result


# USEFUL FUNCTIONS DEFINITIONS
def send_email(from_addr, pwd, to_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.ehlo()
        server.login(from_addr, pwd)
        server.sendmail(from_addr, to_addr, msg.as_string())
        server.quit()

        print('Email sent!')
    except:
        print('Something went wrong...')