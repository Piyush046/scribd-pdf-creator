#!/usr/bin/env python

"""A script to create PDF documents from Scribd pages."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib
import os
import time
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

SCROLL_HEIGHT = 1200
PAGE_WIDTH = 20.7
PAGE_HEIGHT = 29.6

def output_user_string(string):
    """Output a message to the user"""
    print(string)


def get_source_data(name, links_dict):
    """Download the data associated with the page links."""

    # Initialise the PDF.
    c = canvas.Canvas('%s%s' % (name, '.pdf'))

    for key in sorted(links_dict):
        # Download the image file from the link.
        dst = '%s%s' % (str(key), '.jpg')
        urllib.urlretrieve(links_dict[key], dst)
        output_user_string("PDF: Adding " + dst + " from " + links_dict[key])

        # Write the image file to the PDF, and move to the next page.
        c.drawImage(dst, 0, 0, PAGE_WIDTH * cm, PAGE_HEIGHT * cm)
        c.showPage()

        # Remove the source file.
        os.remove(dst)

    # Save the PDF.
    c.save()
    output_user_string("PDF READY.")


def get_source_links(url):
    """Get the page links from the URL."""

    # Start the driver and open the URL.
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')
    driver.get(url)

    # Define a dictionary to hold the returned links.
    #   key: Page number
    #   value: Link to the page's image
    links_dict = {}
    page_count = 0
    scroll_count = 2

    # Get the title and number of pages from the page's Javascript.
    js_dict = driver.execute_script("return Scribd.current_doc")
    js_title = js_dict['title']
    js_page_count = js_dict['page_count']

    while page_count < js_page_count:
        # Create a Javascript scroll command and execute within the page.
        jscript_scroll = "%s %s%s" % ('window.scrollTo(0,', 
                                      str(SCROLL_HEIGHT * scroll_count), 
                                      ');')
        driver.execute_script(jscript_scroll)
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "absimg")))

        # Get the links visible on this page, and add any new links to our
        # dictionary.
        scroll_count += 1
        elements = driver.find_elements_by_class_name('absimg')
        for i in elements:
            link = i.get_attribute('src')
            key = int((link.split('/')[-1]).split('-')[0])
            if key not in links_dict:
                page_count += 1
                links_dict[key] = link
                output_user_string("ADDING " + link)

    # Kill the driver.
    driver.close()
    output_user_string("Successfully added %d pages" % page_count)

    return (links_dict, js_title)


def get_file_url():
    """Query the user for the URL to use."""
    return raw_input('URL to use: ')
#    return "http://www.scribd.com/doc/131321174/Edexcel-Maths-C3"


if __name__ == "__main__":
    # Get the URL and name from the user.
    url = get_file_url()

    # Attempt to get the source links from the URL.
    links_dict, name = get_source_links(url)

    # Attempt to get the source data from the links, and create the PDF.
    get_source_data(name, links_dict)
