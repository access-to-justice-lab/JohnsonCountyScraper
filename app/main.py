import scrape
import sql
import pprint
import time
import sys
import platform
import os


def incrementCasenumber(casenumber):
    firstfour = casenumber[0:4]
    lastnumber = int(casenumber[5:])
    lastnumber += 1
    lastnumber = str(lastnumber)
    while len(lastnumber) < 5:
        lastnumber = "0" + lastnumber
    newcasenumber = firstfour + lastnumber
    return newcasenumber

# This is for easier development without having to launch docker.
def setOSVariables():
    # Reads the environment file and sets the OS variables.
    # Called only on windows computers.
    with open('../env.list') as fp:
        for line in fp:
            key = line.strip('\n').split("=")[0]
            value = line.strip('\n').split("=")[1]
            print(key, value)
            os.environ[key] = value
    # The IP needed from a docker container is different from the one run on windows.
    os.environ['sql_ip'] = 'localhost'
    print(os.environ['sql_user'])
    if(len(sys.argv) != 3):
        sys.exit("Wrong number of arguments")
    else:
        os.environ['startingcase'] = sys.argv[1]
        os.environ['limit'] = sys.argv[2]

if __name__ == '__main__':
    # Get the initial Cookies and ASPX Parameters
    # This way we can use the same session ID for multiple requests.
    # 20CR00095
    print("Starting the Joco Scraper")
    # Sets the os environment variables for easier testing.
    if(platform.system() == 'Windows'):
        setOSVariables()

    # if(len(sys.argv) > 2):
    #     # Means we have a case number
    #     casenumber = sys.argv[1]
    #     limit = int(sys.argv[2])
    # else:
    #     print("Please include system arguments: main.py [casenumber] [limit]")
    if('startingcase' in os.environ and 'limit' in os.environ):
        # Means we have a case number
        casenumber = os.environ['startingcase']
        limit = int(os.environ['limit'])
    else:
        print("docker run --env-file env.list --env startingcase=20CR00830 --env limit=5 -t --name joco joco_server")
        print(os.environ['startingcase'],os.environ['limit'])
        sys.exit(1)


    cookiesandhtml = scrape.getCookiesandHTML()
    cookies = cookiesandhtml['Cookies']
    base_aspx_headers = scrape.parseASPXParameters(cookiesandhtml['HTML'])
    count = 1

    while count <= limit:
        print("Searching Case Number:",casenumber)
        try:
            # Ever 50 cases grab a new session id.
            if(count % 50 == 0):
                print("Getting new session" + str(count))
                cookiesandhtml = scrape.getCookiesandHTML()
                cookies = cookiesandhtml['Cookies']
                base_aspx_headers = scrape.parseASPXParameters(cookiesandhtml['HTML'])

            # The charges page is where we start with a case number request
            chargehtml = scrape.getChargeHTML(cookies, casenumber, base_aspx_headers)

            if(chargehtml == None):
                #If we can't find the charges page there is no case.
                print(casenumber,"not found")
            else:
                aspxheaders = scrape.parseASPXParameters(chargehtml) # Need to get new aspxheader for each tab query

                # Get the HTML from the tabs
                casehistoryhtml = scrape.getTabHTML(cookies, {'btmCRROA': 'CASE HISTORY (ROA)'}, aspxheaders)

                accountingHTML = scrape.getTabHTML(cookies, {'btmcrAccounting': 'Accounting'}, aspxheaders)
                calendarHTML = scrape.getTabHTML(cookies, {'btmcrCalendar': 'Calendar'}, aspxheaders)
                othercaseshtml = scrape.getTabHTML(cookies, {'btmcrOtherCases': 'Other Cases'}, aspxheaders)

                # Parse Everything
                fullcase = scrape.parseHTML(chargehtml, casehistoryhtml, accountingHTML, calendarHTML, othercaseshtml)

                # pp = pprint.PrettyPrinter(indent=4)
                # pp.pprint(fullcase)
                sql.saveCase(casenumber, fullcase)
            count += 1
            casenumber = incrementCasenumber(casenumber)
            time.sleep(1)
        except Exception as e:
            print(e)
            if(fullcase != None):
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(fullcase)
            print(casenumber)
            print(e)
            sys.exit()