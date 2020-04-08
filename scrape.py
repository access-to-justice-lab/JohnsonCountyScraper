import requests
from lxml.html import fromstring
import bs4
import sys
import hashlib
import json

from unicodedata import normalize
from sql import saveCase

def getCookiesandHTML():
    url = "http://www.jococourts.org/"
    #Make the HTTP Request
    try:
        resp = requests.get(url)
        title = fromstring(resp.content).findtext('.//title').strip()
        aspnet = resp.cookies['ASP.NET_SessionId']
        bigip = resp.cookies['BIGipServerwww.jococourts.org_pool']
        # Iterate over items in dict and print line by line
        # [print(key, value) for key, value in resp.headers.items()]

        return {"HTML":resp.text,"Cookies":{'ASP.NET_SessionId':aspnet,'BIGipServerwww.jococourts.org_pool':bigip}}
    except Exception as e:
        raise e
def getChargeHTML(cookies,casenumber,aspxheaders):
    url = "http://www.jococourts.org/"
    headers = {
            'referer' :'http://www.jococourts.org/',
            'origin' :'http://www.jococourts.org',
            'host' :'www.jococourts.org',
            'Upgrade-Insecure-Requests':'1'
    }
    params = {
        '__LASTFOCUS': '',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        'txtCaseNo': casenumber,
        'txtLName': '',
        'txtFName': '',
        'rdoCriminalCivil': 'Criminal/Traffic',
        'BtnsrchExact': 'Case Number/Exact Name Search'}
    params.update(aspxheaders)
    cookieparams = {'ASP.NET_SessionId':cookies['ASP.NET_SessionId']}
    # Make the HTTP Request
    try:
        # resp = requests.post(url,data=params,cookies=cookieparams,timeout = 120)
        resp = requests.post(url, data=params, headers=headers, timeout=120,cookies=cookieparams)
        title = fromstring(resp.content).findtext('.//title').strip()
        if(title == 'Johnson County Kansas District Court Document Search'):
            #Means Case Not Found we're back on the homepage
            return None
        elif(title == 'Disposition'):
            #Means we found the page
            return resp.text
        else:
            #Not sure what this means
            print("Unknown Title")
            sys.exit(0)
    except Exception as e:
        raise e

def getTabHTML(cookies,tab,aspxheaders):
    url = "http://www.jococourts.org/crDispo.aspx"
    headers = {
            'referer' :'http://www.jococourts.org/crDispo.aspx',
            'origin' :'http://www.jococourts.org',
            'host' :'www.jococourts.org',
            'Upgrade-Insecure-Requests':'1'
    }
    params = {}
    params.update(tab) #This adds the button pushed parameter
    params.update(aspxheaders)
    cookieparams = cookies
    # Make the HTTP Request
    try:
        # resp = requests.post(url,data=params,cookies=cookieparams,timeout = 120)
        resp = requests.post(url, data=params, headers=headers, timeout=120,cookies=cookieparams)
        title = fromstring(resp.content).findtext('.//title').strip()
        if(title == 'Johnson County Kansas District Court Document Search'):
            #Means Case Not Found we're back on the homepage
            return None

        elif(title in ['CASE HISTORY (ROA)', 'Payment Information','Calendar', 'Other Cases']):
            #Means we found the page
            return resp.text
        else:
            #Not sure what this means
            print("Unknown Title")
            sys.exit(0)
    except Exception as e:
        raise e

def parseASPXParameters(html):
    soup = bs4.BeautifulSoup(html,'lxml')
    aspx = {
        '__VIEWSTATE':'',
        '__VIEWSTATEGENERATOR':'',
        '__EVENTVALIDATION':''
    }
    for aspxheader in aspx:
        field = soup.find(id=aspxheader)
        if (field != None and field.has_attr('value')):
            # Check to make sure it has a value field
            aspx[aspxheader] = field['value']
    return aspx
def parseHTML(chargehtml,casehistoryhtml,accountinghtml,calendarhtml,othercaseshtml):
    # Parse the main page with the charge information
    fullcase = {}

    fullcase['caseinfo'] = parseCaseHeaderInformation(chargehtml)
    # print(hashlib.md5(json.dumps(fullcase['caseinfo']).encode('utf-8')).hexdigest())

    fullcase['charges'] = parseChargeInformation(chargehtml)
    fullcase['sentence'] = parseSentenceInfo(chargehtml)

    # Next parse the page with the case history information
    fullcase['case history'] = parseCaseHistory(casehistoryhtml)

    # Parse Accounting Page
    fullcase['accounting'] = parseAccountingHTML(accountinghtml)

    # Parse Calendar Page
    fullcase['calendar'] = parseCalendarHTML(calendarhtml)

    # Parse Other Cases
    fullcase['othercases'] = parseOtherCasesHTML(othercaseshtml)
    return fullcase
def parseCaseHeaderInformation(chargehtml):
    #Look up the basic case filing information and defendant information.
    #This is all held in the input tags at the top.
    #Cycle through all the IDs of the input tags and capture the value attribute or leave blank.
    soup = bs4.BeautifulSoup(chargehtml,'lxml')
    caseinfo = {
        "CaseNo":None,
        "LName":None,
        "FName":None,
        "MName":None,
        "Sufix":None,
        "SexRaceDob":None,
        "ProbOfficer":None,
        "Div":None,
        "Defendent":None,
        "Prosecutor":None,
        "JudgeName":None,
        "Status":None
    }
    for header in caseinfo:
        field = soup.find(id='txt'+header)
        if(field != None and field.has_attr('value')):
            #Check to make sure it has a value field
            caseinfo[header] = field['value']

    #Seperate Race/Gender and DOB
    #Example W/F 01/23/62
    if(caseinfo["SexRaceDob"] != "" and caseinfo["SexRaceDob"] != None):
        if(" " in caseinfo["SexRaceDob"]):
            sr = caseinfo["SexRaceDob"].split(" ")[0]
            caseinfo["DOB"] = caseinfo["SexRaceDob"].split(" ")[1]
            if("/" in sr):
                caseinfo['Race'] = sr.split("/")[0]
                caseinfo['Sex'] = sr.split("/")[1]

    return caseinfo
def parseChargeInformation(chargehtml):
    #Grabs the charge and dispo information from the last table
    #Cycles through all the rows and assigns them to the table headers.
    #Hopefully the table headers don't change!
    #Note there are some charges that are "Amended" but look like a second charge. 97CR00090
    soup = bs4.BeautifulSoup(chargehtml, 'lxml')
    return parseLastTable(soup,headers= [
        'Charge Number',
        'Section',
        'Date',
        'Title',
        'ACS',
        'Drug',
        'PL',
        'Finding',
        'TP',
        'LVL',
        'PN',
        'Sent Date',
    ],page='Charge Info')
def parseSentenceInfo(chargehtml):
    soup = bs4.BeautifulSoup(chargehtml, 'lxml')
    sentenceinfo = {
        "OriJail":None,
        "SuspJail":None,
        "FinJail":None,
        "OriProb":None
    }
    for header in sentenceinfo:
        field = soup.find(id='txt'+header)
        if(field != None and field.has_attr('value')):
            #Check to make sure it has a value field
            sentenceinfo[header] = field['value']
    return sentenceinfo
    #[print(key,":", value) for key, value in sentenceinfo.items()]
def parseCaseHistory(casehistoryhtml):
    #Gets the case history notes from the html
    soup = bs4.BeautifulSoup(casehistoryhtml, 'lxml')
    return parseLastTable(soup,headers = [
        'Date',
        'Note'
    ],page='Case History')
def parseAccountingHTML(accountingHTML):
    #Gets the case history notes from the html
    soup = bs4.BeautifulSoup(accountingHTML,'lxml')
    return parseLastTable(soup,headers = [
        'Assessed Type',
        'Assessed Amount',
        'Amount Paid',
        'Balance'
    ],page='Accounting')
def parseCalendarHTML(calendarhtml):
    soup = bs4.BeautifulSoup(calendarhtml,'lxml')
    return parseLastTable(soup,headers=[
        'Court Date',
        'Court Time',
        'Division',
        'Proceeding Type'
    ],page='Calendar')
def parseOtherCasesHTML(othercaseshtml):
    soup = bs4.BeautifulSoup(othercaseshtml,'lxml')
    return parseLastTable(soup,headers=[
        'Other Cases',
        'Related Type'
    ],page='Other Cases')
def parseLastTable(soup,headers,page):
    #Returns the information based on the last table
    #This works for accounting, history, and charges
    #Need to add in a feature that will checked if there are an unexpected number of columns.
    allitems = []
    givenheaders = headers
    dispotable = soup.find_all('table')[-1]
    rows = dispotable.find_all("tr")

    #Check if <h2> No xxx Found </h2> is set.
    h2 = soup.find("h2")
    if(h2 != None and h2.text[0:2] == "No"):
        # Means we dont have any information for this. See 97CR00097 on the other cases tab.
        return []

    # Get headers if they exist (not it Case History)
    if(rows[0].find('th') != None):
        #Means we have headers
        headers = [] # Use the table headers
        headersexist = True
        cells = rows[0].find_all('th')
        for cell in cells:
            headers.append(cell.text)
        if(page == 'Charge Info' and headers[0] == ""):
            # For some reason there is no row header for the first column on charges.
            headers[0] = "Charge Count"
    else:
        # Means we go with the headers we're given
        headersexist = False

    #Check if Headers have different lengths. If they do we need to investigate.
    if(len(givenheaders) != len(headers)):
        print("WARNING: We don't have same headers",page)
        sys.exit(1)
    # Start parsing actual information
    x = 0 # Represents which row
    for row in rows:
        if(headersexist == True):
            # Skip the first row if headers exist.
            headersexist = False # Otherwise we end up continuing everytime
            continue
        y = 0 # Where in the row we are
        cells = row.find_all('td')
        allitems.append({})
        for cell in cells:
            if(normalize('NFKD',cell.text) == "" or normalize('NFKD',cell.text) == u' '):
                allitems[x][headers[y]] = None
            else:
                allitems[x][headers[y]] = normalize('NFKD',cell.text).strip()
            y += 1
        x += 1
    # for singleitem in allitems:
    #     [print(key,":", value) for key, value in singleitem.items()]
    return allitems

