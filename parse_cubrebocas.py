import pandas as pd
from PyPDF2 import PdfFileReader
import tabula
import numpy as np
from datetime import datetime
import os
import locale
import re

locale.setlocale(locale.LC_ALL, 'es_ES')

download_folder    = "reports"
save_folder        = "parsed"
folder_of_download = os.getcwd() + "/" + download_folder
data_frame = []

for pdf_name in os.listdir(folder_of_download):

    if pdf_name.endswith(".pdf"):

        date = datetime.strptime(pdf_name,"%d_%B_%Y.pdf")

        #After october 24th they stopped measuring face masks
        if date <= datetime.strptime("24/09/2021","%d/%m/%Y"):

            print(pdf_name)

            pdf      = PdfFileReader(open(os.path.join(folder_of_download, pdf_name), 'rb'))
            max_page = pdf.getNumPages()

            # extract text and do the search
            flag_search = False
            for i in range(0, max_page):
                page   = pdf.getPage(i)
                text   = page.extractText()
                search = re.search(r'Colonias con mayor uso de cubrebocas', text)
                if search:
                    pagemin = i + 1
                    flag_search = True

                search = re.search(r'Colonias con menor uso de cubrebocas', text)
                if search:
                    pagemax = i + 1

            if pagemin >  max_page and not flag_search:
                pagemin = max_page
                pagemax = max_page - 1

            try:
                #Obtain the ones with less utilization
                tbl = tabula.read_pdf(os.path.join(folder_of_download, pdf_name), pages=pagemin, guess = False,
                                        stream = True, encoding="utf-8",output_format="dataframe",
                                        area = (80, 240, 80 + 250, 230 + 400),
                                        columns = (240,320,470))
                df = tbl[0]
                df['% uso'] = df['% uso'].str.rstrip('%').astype(float) / 100.0
                minimo_1 = np.nanmin(df['% uso'])
                maximo_1 = np.nanmax(df['% uso'])

                #Obtain the ones with more utilization
                tbl = tabula.read_pdf(os.path.join(folder_of_download, pdf_name), pages=pagemax, guess = False,
                                        stream = True, encoding="utf-8",output_format="dataframe",
                                        area = (80, 240, 80 + 250, 230 + 400),
                                        columns = (240,320,470))
                df = tbl[0]
                df['% uso'] = df['% uso'].str.rstrip('%').astype(float) / 100.0
                minimo_2 = np.nanmin(df['% uso'])
                maximo_2 = np.nanmax(df['% uso'])

                if minimo_1 < minimo_2:
                    minimo = minimo_1
                else:
                    minimo = minimo_2

                if maximo_2 < maximo_1:
                    maximo = maximo_1
                else:
                    maximo = maximo_2

                data_frame.append(
                    {
                        "Minimo uso cubrebocas": minimo,
                        "Maximo uso cubrebocas": maximo,
                        "Fecha (dmy)": date.strftime("%d/%m/%Y"),
                    }
                )
            except:
                print("Unable to parse " + pdf_name)


data_frame     = pd.DataFrame(data_frame)
folder_of_save = os.path.join(os.getcwd(), save_folder)
data_frame.to_csv(os.path.join(folder_of_save,"Cubrebocas.csv"))
