#!/usr/bin/env python

"""A script to create PDF documents from Scribd pages.

See the page source of "http://www.scribd.com/doc/131321174/Edexcel-Maths-C3"
for an idea of what we're parsing with this script.

"""
import re
import os
import urllib
import requests
from BeautifulSoup import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# PDF attributes
PAGE_WIDTH = 20.7
PAGE_HEIGHT = 29.6

def output_user_string(string):
    """Output a message to the user"""
    print(string)


def convert_link_to_jpg(link):
    """Replace substrings. May be a no-op"""
    link = link.replace('pages', 'images')
    link = link.replace('jsonp', 'jpg')
    
    return link


def create_pdf(title, link_list):
    """Download the data associated with the page links."""

    # Initialise the PDF.
    pdf_title = '%s%s' % (title, '.pdf')
    c = canvas.Canvas(pdf_title)
    output_user_string("PDF INFO: Creating PDF '%s'" % pdf_title)

    index = 0
    page_count = 0
    for item in link_list:
        index += 1
        dst = '%s%s' % (str(index), '.jpg')        

        try:
            urllib.urlretrieve(item, dst)
            c.drawImage(dst, 0, 0, PAGE_WIDTH * cm, PAGE_HEIGHT * cm)
        except:
            try:
                item = item.replace("jpg", "png")
                dst = dst.replace("jpg", "png")
                urllib.urlretrieve(item, dst)
                c.drawImage(dst, 0, 0, PAGE_WIDTH * cm, PAGE_HEIGHT * cm)
            except:
                output_user_string("PDF ERROR: Couldn't write image %s" % dst)
                continue
        
        c.showPage()
        page_count += 1
        os.remove(dst)

    # Save the PDF.
    c.save()
    output_user_string("PDF INFO: Wrote %d pages" % page_count)


def get_source_links(url):
    """Get the page links from the URL."""

    # Open the URL and download our soup.
    page = requests.get(url, timeout=5)
    soup = BeautifulSoup(page.text)

    # Get the title of the page.
    title = soup.title.string

    # Scrape the links to the JPEG images.
    link_list = []
    jpg_list = soup.findAll('img', {'class':'absimg'})
    for item in jpg_list:
        link_list.append(item.get('orig'))

    # Scrape the links to the JSON objects.
    # The links are in the following form:
    # "https://html2-f.scribdassets.com/7ns76vwfr428hze3/pages/191-5318e2f8fc.jsonp";
    js_text = soup.findAll('script', text=re.compile("jsonp"))
    regex = re.compile('http(.+?)jsonp')
    for item in js_text:
        json_link = regex.search(item).group(0)
        if json_link != None:
            # Assume that the image will be JPEG format.
            link_list.append(convert_link_to_jpg(json_link))

    output_user_string("QUEUE INFO: Added %d pages" % len(link_list))
    return (title, link_list)


def get_file_urls():
    """Query the user for the URL(s) to use."""
    return raw_input('URLs to use (comma delimited): ').split(',')


def main():
    """Main entrant function."""

    # Get the URLs from the user.
    url_list = get_file_urls()

    # Get the source links from the URL.
    for item in url_list:
        output_user_string("\nINFO: Processing '%s'" % item)
        title, link_list = get_source_links(item)
        
        # Create the PDF.
        create_pdf(title, link_list)


if __name__ == "__main__":
    main()
