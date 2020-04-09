from datetime import datetime
from datetime import date
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
import os

# This file connects to the mysql database and saves the case information.
# The credentials are gathered from the os.environ field designed to be passed by docker.

Base = declarative_base()

class CaseInfo(Base):
    __tablename__ = 'caseinfo'
    id = db.Column(db.Integer, primary_key=True,)
    casenumber = db.Column(db.String(255),unique=True)
    def_fname=db.Column(db.String(255))
    def_mname=db.Column(db.String(255))
    def_lname=db.Column(db.String(255))
    dob=db.Column(db.DATE)
    race=db.Column(db.String(255))
    sex=db.Column(db.String(255))
    sexracedob=db.Column(db.String(255))
    probofficer=db.Column(db.String(255))
    sufix=db.Column(db.String(255))
    prosecutor=db.Column(db.String(255))
    defendantattorney=db.Column(db.String(255))
    division=db.Column(db.String(255))
    judge=db.Column(db.String(255))
    status=db.Column(db.String(255))
    timestamp=db.Column(db.TIMESTAMP)

class Charges(Base):
    __tablename__ = 'charges'
    id = db.Column(db.Integer, primary_key=True)
    casenumber = db.Column(db.String(255))
    acs = db.Column(db.String(255))
    chargecount = db.Column(db.String(255))
    date = db.Column(db.DATE)
    drug = db.Column(db.String(255))
    finding = db.Column(db.String(255))
    lvl = db.Column(db.String(255))
    pl = db.Column(db.String(255))
    pn = db.Column(db.String(255))
    section = db.Column(db.String(255))
    sentdate = db.Column(db.DATE)
    tp = db.Column(db.String(255))
    title = db.Column(db.String(255))

class OtherCases(Base):
    __tablename__ = 'othercases'
    id = db.Column(db.Integer,primary_key=True)
    casenumber = db.Column(db.String(255))
    othercase = db.Column(db.String(255))
    relatedtype = db.Column(db.String(255))

class CaseHistory(Base):
    __tablename__ = 'casehistory'
    id = db.Column(db.Integer,primary_key=True)
    casenumber = db.Column(db.String(255))
    notedate = db.Column(db.DATE)
    note = db.Column(db.TEXT)

class Calendar(Base):
    __tablename__ = 'calendar'
    id = db.Column(db.Integer,primary_key=True)
    casenumber = db.Column(db.String(255))
    courtdate = db.Column(db.DATE)
    courttime = db.Column(db.String(255))
    division = db.Column(db.String(255))
    proceedingtype = db.Column(db.String(255))

class Accounting(Base):
    __tablename__ = 'accounting'
    id = db.Column(db.Integer,primary_key=True)
    casenumber = db.Column(db.String(255))
    amountpaid = db.Column(db.DECIMAL(20,2))
    assessedamount = db.Column(db.DECIMAL(20,2))
    assessedtype = db.Column(db.String(255))
    balance = db.Column(db.DECIMAL(20,2))

class Sentence(Base):
    __tablename__ = 'sentence'
    id = db.Column(db.Integer,primary_key=True)
    casenumber = db.Column(db.String(255))
    finjail = db.Column(db.String(255))
    orijail = db.Column(db.String(255))
    oriprob = db.Column(db.String(255))
    suspjail = db.Column(db.String(255))

def fix4YearDate(date):
    if(date == None or date == ""):
        return None
    else:
        return datetime.strptime(date,'%m/%d/%Y')
def fix2YearDate(givendate):
    if(givendate == "" or givendate is None):
        return None
    else:
        # Since we only have two digit year we need to reformat so the year is properly recorded.
        curr_year = str(date.today().year)[2:4]
        givendate_year = givendate.split("/")[2]
        if(int(givendate_year) > int(curr_year)):
            # Means the person was born in 19--
            givendate_year = '19'+givendate_year
        else:
            # Means the person was born in the 21st century need to add 20
            givendate_year = '20' + givendate_year
        corrected_date = givendate.split("/")[0] + "/" + givendate.split("/")[1] + "/" + givendate_year
        return datetime.strptime(corrected_date,'%m/%d/%Y')

def testConnection():
    try:
        engine = db.create_engine(
            "mysql+pymysql://" + os.environ['sql_user'] + ":" + os.environ['sql_password'] + "@" + os.environ['sql_ip'] + "/" + os.environ['sql_schema'] +"?charset=utf8mb4&binary_prefix=true")
        engine.connect()
        return True
    except OperationalError as cred:
        print("Probably bad credentials")
        print(os.environ['sql_user'])
        print(cred)
        return False
    except Exception as e:
        print("Other error")
        print(os.environ['sql_user'])
        print(e)
        return False

def saveCase(casenumber,casedictionary):
    engine = db.create_engine(
        "mysql+pymysql://" + os.environ['sql_user'] + ":" + os.environ['sql_password'] + "@" + os.environ['sql_ip'] + "/johnsoncounty?charset=utf8mb4&binary_prefix=true")
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    caseinfodictionary = casedictionary['caseinfo']

    # Add Case Header Information
    caseinfosql = CaseInfo(
        casenumber=caseinfodictionary['CaseNo'],
        def_fname=caseinfodictionary['FName'],
        def_mname=caseinfodictionary['MName'],
        def_lname=caseinfodictionary['LName'],
        sufix=caseinfodictionary['Sufix'],
        dob=fix2YearDate(caseinfodictionary['DOB']),
        race=caseinfodictionary['Race'],
        sex=caseinfodictionary['Sex'],
        sexracedob=caseinfodictionary['SexRaceDob'],
        probofficer=caseinfodictionary['ProbOfficer'],
        prosecutor=caseinfodictionary['Prosecutor'],
        defendantattorney=caseinfodictionary['Defendent'],
        division=caseinfodictionary['Div'],
        judge=caseinfodictionary['JudgeName'],
        status=caseinfodictionary['Status'],
        timestamp=datetime.now())
    session.add(caseinfosql)

    # Add Charges
    for charge in casedictionary['charges']:
        tempcharge = Charges(
            casenumber=caseinfodictionary['CaseNo'],
            acs=charge['ACS'],
            chargecount=charge['Charge Count'],
            date=fix2YearDate(charge['Date']),
            drug=charge['Drug'],
            finding=charge['Finding'],
            lvl=charge['LVL'],
            pl=charge['PL'],
            pn=charge['PN'],
            section=charge['Section'],
            sentdate=fix4YearDate(charge['Sent Date']),
            tp=charge['TP'],
            title=charge['Title']
        )
        session.add(tempcharge)

    # Add Other Cases
    for othercase in casedictionary['othercases']:
        tempot = OtherCases(
            casenumber=caseinfodictionary['CaseNo'],
            othercase=othercase['Other Cases'],
            relatedtype=othercase['Related Type'])
        session.add(tempot)

    # Add Case History
    for casenote in casedictionary['case history']:
        casetemp = CaseHistory(
            casenumber=caseinfodictionary['CaseNo'],
            notedate=fix4YearDate(casenote['Date']),
            note=casenote['Note'])
        session.add(casetemp)

    # Add Calendar
    for calendarevent in casedictionary['calendar']:
        caltemp = Calendar(
            casenumber=caseinfodictionary['CaseNo'],
            courtdate=fix2YearDate(calendarevent['Court Date']),
            courttime = calendarevent['Court Time'],
            division = calendarevent['Division'],
            proceedingtype = calendarevent['Proceeding Type'])
        session.add(caltemp)

    # Add Accounting
    for accountingevent in casedictionary['accounting']:
        acct = Accounting(
            casenumber=caseinfodictionary['CaseNo'],
            amountpaid=accountingevent['AMOUNT PAID'],
            assessedamount = accountingevent['ASSESSED AMOUNT'],
            assessedtype = accountingevent['ASSESSED TYPE'],
            balance = accountingevent['BALANCE'])
        session.add(acct)

    # Add Sentence
    sent = Sentence(
        casenumber = caseinfodictionary['CaseNo'],
        finjail = casedictionary['sentence']['FinJail'],
        orijail = casedictionary['sentence']['OriJail'],
        oriprob = casedictionary['sentence']['OriProb'],
        suspjail = casedictionary['sentence']['SuspJail']
    )
    session.add(sent)
    session.commit()