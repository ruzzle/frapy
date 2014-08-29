'''
Created on 11 jan. 2013

@author: marinus
'''

from bs4 import BeautifulSoup
from dateutil import parser as dateparser
import re

__all__= ["xpath2text", "text2date"]

def xpath2text(selector, xpath, regex=None):
    snippets = selector.xpath(xpath).extract()
    if regex and snippets:
        matches = [m for m in [re.search(regex, snippet) for snippet in snippets] if m]
        if matches:
            return matches.pop()
        else:
    	    raise Exception("Geen matches met regex: '%s' in tekst: '%s'" % (regex, " ".join(snippets)))
    else:
	    return " ".join(_snippet_to_text(snippet) for snippet in snippets)

def text2date(text):
    try:
        text = re.sub('[^\x20-\x7E]', '', text)
        return dateparser.parse(text)
    except ValueError:
        raise Exception('Ongeldige datum string %s' % text)

def _snippet_to_text(snippet):
    soup = BeautifulSoup(snippet)
    text = ' '.join(soup.findAll(text=True)).strip()
    return text
    
