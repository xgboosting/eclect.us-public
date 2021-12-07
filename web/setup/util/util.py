import re, math, os, requests
import pandas as pd
from bs4 import BeautifulSoup
#from summarizer import Summarizer
#from summarizer.coreference_handler import CoreferenceHandler

import urllib.request as request
from contextlib import closing
import shutil

level = os.getenv('LEVEL')
millnames = ['',' Thousand',' Million',' Billion',' Trillion'] 
REMOVE_ATTRIBUTES = [
    'lang','language','onmouseover','onmouseout','script','style','font',
    'dir','face','size','color','style','class','width','height','hspace',
    'border','valign','align','background','bgcolor','text','link','vlink',
    'alink','cellpadding','cellspacing', 'colspan']
class util:

    def getNasdaqTraded(self): 
        try:
            with closing(request.urlopen('ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqtraded.txt')) as r:
                with open('nasdaqtraded.txt', 'wb') as f:
                    shutil.copyfileobj(r, f)
            df = pd.read_csv("nasdaqtraded.txt", delimiter='|')
        except:
            df = pd.read_csv("/Users/cg/eclect.us/web/setup/nasdaqtraded.txt", delimiter='|')
        df['cleanedName'] = df['Security Name'].apply(lambda x: self.cleanSecurityName(x) )
        return df

    def cleanTitle(self, title):
        title = re.findall(r'- ([A-Za-z.&\- ,]*)', title)
        title = title[0].strip()
        title = title.replace('.', '')
        title = title.replace(',', '')
        return title.lower()
        
    def cleanSecurityName(self, securityName):
        try:
            securityName = securityName.replace('.', '')
            return securityName.lower()
        except:
            return 'error'

    def getAMatch(self, cleanedTitle, df):
        matches = []
        try:
            senToMatch = cleanedTitle.split()
            for x, row in df.iterrows():
                sentence = row['cleanedName'].split()
                sent = sentence[0].replace('.', '')
                sent = sent.replace(',', '')
                sent = sent.replace("'", '')
                if senToMatch[0] == sent:
                    matches.append(row)
            if len(matches) > 1:
                for m in matches:
                    sentence = m['cleanedName'].split()
                    try:
                        sent = sentence[1].replace('.', '')
                        sent = sent.replace(',', '')
                        sent = sent.replace("'", '')
                        if senToMatch[1] == sent:
                            return m['Symbol']
                    except IndexError:
                        print("index error")
                        continue
            elif len(matches) == 1:
                return matches[0]['Symbol']
            else:
                return
        except Exception as e_e:
            print(matches)
            print(e_e)
            print("getAMatch")
        
    def millify(self, n):
        try:
            n = float(n)
            millidx = max(0,min(len(millnames)-1, int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
            return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
        except Exception as e_e:
            print('millify')
            print(e_e)


    def getFiling(self, url):
        try:
            print(url)
            url = re.findall(r'(.+)-index', url)
            url = url[0].strip()
            url = f"{url}.txt"
            print(url)
            headers = { 'User-Agent': 'https://eclect.us/ rss feed quarterly report downloader', 'From': 'gonnellcough@gmail.com'}
            return requests.get(url, headers=headers).text
        except:
            return 'getFiling error'
        

    def removeFilingJunk(self, s):
        s = s.replace('\n', ' ')
        s = s.replace('\xa0', ' ')
        s = s.replace('>', '')
        return re.sub(r'\s+', ' ', s)

    def hasNumbers(self, inputString):
        return any(char.isdigit() for char in inputString)

    def removeSpaces(self, string): 
        pattern = re.compile(r'\s+') 
        return re.sub(pattern, '_', string)

    def getStartAndEnd(self, soup, itemString):
        start = None
        end = None
        for tag in soup.find_all('a', href=True):
            
            matchingText = self.removeSpaces(tag.text.lower())
            if tag['href'].startswith('#') and start is not None and tag['href'] != start:
                end = tag['href']
                break
            if tag['href'].startswith('#') and matchingText.find(itemString) != -1:
                start = tag['href']
        return start, end
    
    def findMatch(self, text, start="", end=""):
        try:
            start = start.replace('#', '')
            end = end.replace('#', '')
            startMatch = None
            for t in re.finditer(rf"=['\"]({start})['\"]", text):
                startMatch = t
            endMatch = None
            for t in re.finditer(rf"=['\"]({end})['\"]", text):
                endMatch = t
        
            if startMatch and endMatch:
                return text[startMatch.end():endMatch.start()]
            else:
                return "NO_MATCH"
        except Exception as ex:
            print(f"{type(ex).__name__} \n {ex.args}")
            return "NO_MATCH"
    
    def clean(self, text):
        soup = BeautifulSoup(text, 'lxml')
        for t in soup.find_all('table'):
            t.decompose()

        soup.get_text()
        return self.removeFilingJunk(soup.get_text())


    def removeAttrs(self, soup):
        for tag in soup():
            for attribute in REMOVE_ATTRIBUTES:
                del tag[attribute]
        soup = str(soup).replace('\n', ' ')
        soup = soup.replace('\xa0', ' ')
        return soup
    
    def extractTables(self, text):
        tables = []
        soup = BeautifulSoup(text, 'lxml')
        for t in soup.find_all('table'):
            table = self.removeAttrs(t)
            tables.append(table)
        return tables

    def extractSections(self, raw_file): #(file_type = '10-k' or '10-q')
        
        soup = BeautifulSoup(raw_file, 'lxml')

        analysisStart, analysisEnd = self.getStartAndEnd(soup, "discussion_and_analysis")
        qualitativeStart, qualitativeEnd = self.getStartAndEnd(soup, "quantitative_and_qualitative")
        factorsStart, factorsEnd = self.getStartAndEnd(soup, "risk_factors")
        print(f"analysis: {analysisStart}, {analysisEnd}")
        print(f"qualitative: {qualitativeStart}, {qualitativeEnd}")
        print(f"factors: {factorsStart}, {factorsEnd}")

        #if file_type == '10-k':
            #financialsStart, financialsEnd = self.getStartAndEnd(soup, "financial_statements")
        #else:
            #financialsStart, financialsEnd = self.getStartAndEnd(soup, "financial_statements")
            #financialsEnd = analysisStart

        #print(f"financials: {financialsStart}, {financialsEnd}")

        #financialsText = self.findMatch(raw_file, financialsStart, financialsEnd)
        #financialTables = self.extractTables(financialsText)

        analysisText = self.findMatch(raw_file, analysisStart, analysisEnd)
        qualitativeText = self.findMatch(raw_file, qualitativeStart, qualitativeEnd)
        factorsText = self.findMatch(raw_file, factorsStart, factorsEnd)
    
        return self.clean(analysisText), self.clean(qualitativeText), self.clean(factorsText)

