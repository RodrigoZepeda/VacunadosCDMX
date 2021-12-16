#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on December 2021

@author: Rodrigo Zepeda
"""

import pandas as pd
import os
import locale
from sys import argv
from selenium import webdriver
from selenium.webdriver.support.select import Select
import time
import re
from time import sleep
from datetime import date, timedelta
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

direccion_chromedriver = '/usr/local/bin/chromedriver'

download_folder = "reports"
data_folder     = "data/"

print("Descargando pdf")

url_reportes = "https://covid19.cdmx.gob.mx/comunicacion/tipo/Reporte%20diario%20sobre%20COVID-19"

sleep_time = 2  # Tiempo que tarda la página de la UNAM de cambiar ventana
download_time = 2  # Tiempo que tarda en descargarse el archivo en tu red
estatal = True  # Poner como true si quieres datos estatales; como false si quieres clues pero aún no funciona el false

option = webdriver.ChromeOptions()
option.add_argument('--disable-gpu')  # Last I checked this was necessary.
option.add_argument("-incognito")
# option.add_argument("--headless")
folder_of_download = os.getcwd() + "/" + download_folder
option.add_experimental_option("prefs", {
    "download.default_directory": folder_of_download,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing_for_trusted_sources_enabled": False,
    "safebrowsing.enabled": False,
    "plugins.always_open_pdf_externally": True
})


browser = webdriver.Chrome(executable_path=direccion_chromedriver, options=option)
browser.set_window_size(1000, 1000)

locale.setlocale(locale.LC_ALL, 'es_ES')



dates = [datetime.strptime(dateval,"%d_%B_%Y.pdf") for dateval in os.listdir(folder_of_download) if dateval.endswith(".pdf")]

descargar_desde = max(dates) + timedelta(days=1)
descargar_hasta = datetime.today() - timedelta(days=1)

if (descargar_desde < descargar_hasta):

    fechas_descargar = pd.date_range(start=descargar_desde, end=descargar_hasta, freq='D')

    for fecha_analisis in fechas_descargar:
        sleep(sleep_time)
        file_download = None

        while file_download is None:

            print("Downloading " + str(fecha_analisis))
            browser.get(url_reportes)

            year  = str(fecha_analisis.year)
            month = fecha_analisis.strftime("%B").capitalize()
            day   = str(fecha_analisis.day)

            select_year = Select(browser.find_element_by_id("filter_year"))
            select_year.select_by_visible_text(year)

            select_month = Select(browser.find_element_by_id("filter_month"))
            select_month.select_by_visible_text(month)

            select_day  = Select(browser.find_element_by_id("filter_day"))
            select_day.select_by_visible_text(day)

            #Check that there is a link
            try:

                # If there is a link click it!
                sleep(sleep_time)
                elem = browser.find_elements_by_tag_name("a")
                for ele in elem:
                    m = re.search(rf"Reporte(\s*){day}[\w\s]+{month.lower()}", ele.text)
                    if m:
                        ele.click()
                        break


            except NoSuchElementException:

                try:
                    print("File not exists")
                    if int(browser.find_element_by_class_name('current').text) < 1:
                        file_download = False
                    else:
                        file_download = None
                except NoSuchElementException:
                    print("File not found")
                    sleep(sleep_time)

            if (file_download is None):

                try:
                    sleep(sleep_time)
                    file_download = browser.find_element_by_xpath(
                        '//a[contains(text(), "Reporte ' + day + ' de ' + month.lower() + '")]').get_attribute("href")
                    browser.get(file_download)
                except NoSuchElementException:
                    print("Not file download")
                    sleep(sleep_time)

                if file_download is None:
                    print("Downloading file")
                    try:
                        file_download = browser.find_element_by_xpath(
                            "//a[contains(@href, '.pdf')]").get_attribute("href")
                        browser.get(file_download)
                        print("File downloaded")
                    except NoSuchElementException:
                        print("Not file download")
                        sleep(sleep_time)

                if file_download is not None:

                    newname = day + "_" + month + "_" + year + ".pdf"
                    print(newname)
                    sleep(download_time)

                    backslash_position = [pos for pos, char in enumerate(file_download) if char == "/"]

                    download_fname = [filename for filename in os.listdir(folder_of_download) if
                                      filename.startswith("CS")]

                    if len(download_fname) > 0:
                        for filename in download_fname:
                            fpath = os.path.join(folder_of_download, filename)
                            if os.path.getsize(fpath) < 1:
                                os.remove(fpath)
                            else:
                                download_fname = os.path.join(folder_of_download, filename)
                    else:
                        download_fname = [filename for filename in os.listdir(folder_of_download) if
                                          filename.startswith("cs")]
                        for filename in download_fname:
                            fpath = os.path.join(folder_of_download, filename)
                            if os.path.getsize(fpath) < 1:
                                os.remove(fpath)
                            else:
                                download_fname = os.path.join(folder_of_download, filename)

                    # Check file size
                    if os.path.getsize(download_fname) > 0:
                        os.rename(os.path.join(folder_of_download, download_fname),
                                  os.path.join(folder_of_download, newname))

else:
    print("Fechas inválidas probablemente no encuentres nada nuevo aún")
