#!/usr/bin/env ipython -i
from BeautifulSoup import BeautifulSoup
from pprint import pprint as P

from twill.commands import go, showforms, formclear, fv, show, submit
import urllib2

from twill import set_output
from StringIO import StringIO
def showSilently( ):
    set_output(StringIO()) #suppress printing from show
    ret = show()
    set_output(None) 
    return ret


s218 = True

def login():
    if s218:
        page = 'http://129.21.142.218:8008/securesync/login/'
        username = 'JSteacher'
        password = 'poipoi99'
        facility = '0939bcf9d5fe59ff8fde46b5a729a232'
    else:
        page = 'http://129.21.142.118:8008/securesync/login/'
        username = 'knowledgecraft'
        password = 'knowledgecraft'
        facility = 'dbae7005f9b45ce082b5fe0a0985946a'

    print 'Logging In...' 
    go(page)
    print "Forms:"
    showforms()
     
    try:
        # Force try using the first form found on a page.
        formclear('2')
        fv("2", "username", username)
        fv("2", "password", password)
        fv("2", "facility", facility)
        #fv("1", "csrfmiddlewaretoken", '3F1bMuIIM9ERzcp6ceEyFxlT51yJKsK6')
        submit('0')
        content = showSilently()
        print 'debug twill post content:', content
     
    except urllib2.HTTPError, e:
        sys.exit("%d: %s" % (e.code, e.msg))
    except IOError, e:
        print e
    except:
        pass
        
    if "You've been logged in!" in showSilently() :
        print "LOGGED IN!!!!!!!!!!!"
    else:
        print 'NOT LOGGED IN'
    #import pdb; pdb.set_trace()



def queryOnePage(topic='addition-subtraction'): #this is the reference tester.  looks specifically for addition-subtraction
    if s218:
        page = "http://129.21.142.218:8008/coachreports/?group=4e7558068ed856c0a4bc0b5661208863&topic=" + topic
    else:
        page = "http://129.21.142.118:8008/coachreports/?group=1535408fa1415e25a4c781b63e66068c&topic=" + topic
        
    #manually extracted from URL
    print
    go(page)
    print 'Retrieving data for topic', topic
    content = showSilently()
    #print 80*'\n'
    
    soup = BeautifulSoup( content )
    #import pdb; pdb.set_trace()
    
    def between(start_marker, end_marker, raw_string ):
        start = raw_string.index(start_marker) + len(start_marker)
        end = raw_string.index(end_marker, start)
        return raw_string[start:end]
    
    
    tables=soup.findAll('table')
    
    studentSpans = tables[0].findAll('span')
    students  = [span['title'] for span in studentSpans]
    userNames = [between('(',')',student )  for student in students]
    #print 'userNames:::', userNames
    #print
    
    statuses = tables[1]
    statusRows = statuses.findAll('tr')
    exerciseHREFs = [ anchor['href'] for anchor in statusRows[0].findAll('a')]
    
    userStatusRows = statusRows[1:]
    userStatuses={}
    
    for i in range(len(userNames)):
        userStatuses[ userNames[i] ] = [ status['title'] for status in userStatusRows[i].findAll('td') ]    
       
    return {'userNames':userNames, 
            'userStatuses':userStatuses, 
            'exerciseHREFs': exerciseHREFs}



def showData(coachingPageData):  
    """use this to understand or display the data format"""
    D = coachingPageData
    userNames, userStatuses, exerciseHREFs = D['userNames'], D['userStatuses'], D['exerciseHREFs']
    
    TAB = '\t'
    for userName in userNames:
        print
        for i in range(len(exerciseHREFs)):
            print userName, TAB, userStatuses[userName][i], TAB, exerciseHREFs[i]



def getTopicsFromCoachReportsPage( ):
    if s218:
        go( "http://129.21.142.218:8008/coachreports/" )
    else:
        go( "http://129.21.142.118:8008/coachreports/")

    soup = BeautifulSoup( show() )
    #get all the topics (like 'addition-subtraction') from the select widget on the page 
    selectDivs = soup.findAll('div', {'class':'selection'}) 
    divWIthTopics = selectDivs[1]
    optionTags = divWIthTopics.findAll('option')[1:] #first one is empty
    return [option['value'] for option in optionTags]


def sanityCheck():
    #Sanity-check display addition-subtraction to test
    onePage = queryOnePage( topics[0] )
    showData(onePage)

def getShortName( href ):
    return href.split('/')[-2]

#create master list of the exercises associated with each topic.  (It's not determined by the URL!)
def createMemberAndTopicDict():
    memberAndTopic={} 
    """Use this dictionary later to look up the topic, given the member's short name:
       the shortName for the href, /math/arithmetic/addition-subtraction/basic_addition/e/number_line/ 
       is number_line
       
       NOTE: userStatuses will change.  Probably shouldn't be part returned here.
    """
    for topic in topics:
        D= queryOnePage( topic) 
        userNames, userStatuses, exerciseHREFs = D['userNames'], D['userStatuses'], D['exerciseHREFs']
        for href in D['exerciseHREFs']:
            shortName = getShortName( href)
            memberAndTopic[ shortName ] = topic
            print shortName, '\t\t is in \t', topic
    return memberAndTopic
    

""" OK so at this point, given an exercise shortName, we need to  
        look up the topic 
        query the page for that topic
        get the information about a user's status for that topic by
            finding the ordinal position P of that topic in the exerciseHREFs
            finding  userStatuses[P] for our user
            
"""
def status(userName='JSstudent', href='/math/arithmetic/addition-subtraction/basic_addition/e/number_line/' ):
    shortName = getShortName( href)
    topic = memberAndTopics[ shortName ]
    print shortName, 'is in', topic
    D = queryOnePage(topic)
    userNames, userStatuses, exerciseHREFs = D['userNames'], D['userStatuses'], D['exerciseHREFs']
    #userName = 'user'
    status = userStatuses[ userName ][ exerciseHREFs.index( href ) ]
    return status


login()
print 'This startup process will be a little tedious....'
topics = getTopicsFromCoachReportsPage()
memberAndTopics = createMemberAndTopicDict()
#note usersStatuses shold 

print
print 'TEST QUERY'
if s218:
    print ">>>status('JSstudent', '/math/arithmetic/addition-subtraction/basic_addition/e/number_line/')"
    print  'Test status:', status('JSstudent', '/math/arithmetic/addition-subtraction/basic_addition/e/number_line/') 
else:
    print ">>>status('test_user', '/math/arithmetic/addition-subtraction/basic_addition/e/number_line/')"
    print  'Test status:>>>', status('user', '/math/arithmetic/addition-subtraction/basic_addition/e/number_line/') 

"""
KALITE status querier. 
When heavily used, this put an unnecessary load on the KALITE server:
If some server instance  just checked less than a second ago, its uncessary to requery the KALITE server.
Some kind of cacheing woudl be well-advised.
"""