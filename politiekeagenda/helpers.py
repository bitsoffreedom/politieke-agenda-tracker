import os
import re
import hashlib
import urllib
import urllib2
import urlparse

import lxml.html

from datetime import datetime, timedelta

from config import *

def retrieve_if_not_exists(url, bypass_cache=False):
    url_object = urlparse.urlparse(url)
    
    filename = hashlib.md5(urllib.quote_plus(url)).hexdigest()
    target_path = os.path.join(data_directory, filename)
    
    if bypass_cache or not os.path.exists(target_path):
        print "Retrieving {0}...".format(url)
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            content = response.read()
            with open(target_path, "wb") as output_file:
                output_file.write(content)
        except urllib2.URLError, ex:
            print "Error while retrieving {0}".format(url)
            raise ex
    
    document = lxml.html.parse(target_path).getroot()
    document.make_links_absolute(url)

    return document

def date_string_to_datetime(date_string):
    pattern = re.compile("""
        (?P<date>[0-9]+[ ][^ ]+[ ][0-9]{4})
        (?:
            .*
            (?:
                (?:circa)?[ ]
                (?P<start_time>[0-9]+\.[0-9]+)
                (?:[ ]-[ ](?P<end_time>[0-9]+\.[0-9]+))?
            )
        )?
    """, re.VERBOSE)
    #~ print date_string
    
    matches = re.match(pattern, date_string).groupdict()
    date = start_date = end_date = None
    
    date = datetime.strptime(matches["date"], "%d %B %Y")
    if matches["start_time"] != None: 
        hours, minutes = map(int, matches["start_time"].split("."))
        date = start_date = date + timedelta(hours=int(hours), minutes=int(minutes))
    if matches["end_time"] != None: 
        hours, minutes = map(int, matches["end_time"].split("."))
        end_date = date + timedelta(hours=int(hours), minutes=int(minutes))
        
    return (date, start_date, end_date)
    
if __name__ == "__main__":
    test_values = [
        "17 april 2012",
        "20 maart 2012 circa 15.00 uur",
        "17 april 2012 15.00 - 16.00 uur",
        "20 maart 2012 aansluitend aan de gezamenlijke vergadering van V&J en BIZA/AZ",
        "20 maart 2012 aansluitend aan de gezamenlijke vergadering met de commissie voor BZK/AZ (circa 14.30 uur)"
    ]

    for date_string in test_values:
        print date_string_to_datetime(date_string)

def matches(keywords, content):
    keywords = [multiple_replace({"*": "[^ ]+"}, keyword) for keyword in keywords]
    keywords_regex = re.compile(ur"({0})".format("|".join([ur"\b{0}\b".format(keyword) for keyword in keywords])), re.IGNORECASE)
    keywords_matched = set(re.findall(keywords_regex, content))
    
    if len(keywords_matched) > 0: 
        content = re.sub(keywords_regex, ur'<span class="highlight">\1</span>', content)
    
    return (len(keywords_matched) > 0, content, keywords_matched)

def cleanup_html(html):
    def process_element(element):
        for child_element in element.iterchildren():
            try:
                child_element.attrib["style"] = re.sub(r"width[^;]+;?", "", child_element.get("style"))
            except TypeError: pass
            process_element(child_element)
    
    fragment = lxml.html.fragment_fromstring("<div>" + html + "</div>")
    process_element(fragment)
    return lxml.etree.tostring(fragment)

def html2text(html):
    from libs import html2text as _html2text
    _html2text.BODY_WIDTH = 0
    return _html2text.HTML2Text().handle(html)

def multiple_replace(dict, text): 
    regex = re.compile("|".join(map(re.escape, dict.keys())))
    return regex.sub(lambda mo: dict[mo.group(0)], text) 
