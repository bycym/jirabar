from jira.client import JIRA
import logging
import time
import os
import json

bitbar_header = ['BB', '---']
# Use your email address as the username
USER="example@example.com"
# Use the token value as the password
# Create an API token here: https://id.atlassian.com/manage/api-tokens
PASSW="dummypassword"
SERVER="https://example.atlassian.net"
QUERY="assignee = currentUser() ORDER BY updatedDate DESC"
TOPRECENT=10
# Adjust title length of a ticket in status
STATUSLENGTH=80
# Adjust title length of a ticket in dropdown menu
TICKETLENGTH=80
NONSPRINT='[Non sprint]'
CACHE_FILE="jira_noti.cache"
CONFIG_FILE="jirabar.json"
TIME_OUT=3

def parseConfigFile():
  print("parseConfigFile")
  config = {}

  global USER
  global PASSW
  global SERVER
  global QUERY
  global TOPRECENT
  global STATUSLENGTH
  global TICKETLENGTH
  global CACHE_FILE
  global TIME_OUT


  if(not os.path.isfile(CONFIG_FILE)):
    print("Create config file")
    config = {
      'jiraUser': USER, 
      'jiraApiKey': PASSW,
      'server': SERVER,
      'query': QUERY,
      'toprecent': TOPRECENT,
      'statuslength': STATUSLENGTH,
      'ticketlength': TICKETLENGTH,
      'cacheFile': CACHE_FILE,
      'timeOut': TIME_OUT
    } 

    with open(CONFIG_FILE, 'w') as configFile: 
      json.dump(config, configFile, sort_keys=True, indent=4)

  else:
    print("Parse config file")
    with open(CONFIG_FILE, 'r') as configFile: 
      config = json.load(configFile)

      USER = config['jiraUser']
      PASSW = config['jiraApiKey']
      SERVER = config['server']
      QUERY = config['query']
      TOPRECENT = config['toprecent']
      STATUSLENGTH = config['statuslength']
      TICKETLENGTH = config['ticketlength']
      CACHE_FILE = config['cacheFile']
      TIME_OUT = config['timeOut']

# Defines a function for connecting to Jira
def connect_jira(log, jira_server, jira_user, jira_password):
  try:
    log.info("Connecting to JIRA: %s" % jira_server)
    jira_options = {'server': jira_server}
    jira = JIRA(timeout=TIME_OUT, options=jira_options, basic_auth=(jira_user, jira_password), max_retries=0)
    return jira

  except Exception as e:
    log.error("Failed to connect to JIRA: %s" % e)
    return None

# Get bitbar status
def get_in_progress_item(issues):
  myIssues=[]
  mySprints={}
  mySprints[NONSPRINT] = []
  bitbar_header = ['']

  ###############################################################################
  ## header rows
  ####################

  ## drop down started
  bitbar_header.append("%s" % ("---"))
  ## refer link to the in progress element
  dashboard = 'LINK_TO_TOP'
  bitbar_header.append("%s" % (dashboard))
  ## dashboard link
  dashboard = 'Dashboard | href=' + SERVER + '/secure/Dashboard.jspa'
  bitbar_header.append("%s" % (dashboard))
  ## add more custom link

  ###############################################################################

  # filter out Closed or Blocked items
  for issue in issues:
    if (str(issue.fields.status) not in ('Closed', 'Blocked', 'New', 'Rejected', 'Test On Hold' , 'Stuck')):
      myIssues.append(issue);
      sprintName = ''
      if(issue.fields.customfield_10007):
        fieldIndex = 0
        if(len(issue.fields.customfield_10007) > 1):
          fieldIndex = 1
        # get sprint name
        if (issue.raw['fields']["customfield_10007"] and issue.raw['fields']["customfield_10007"][0]['name']):
          sprintName = issue.raw['fields']["customfield_10007"][0]['name']
        if(sprintName != ''):
          mySprints[sprintName] = []

  myIssues.sort(key=lambda x: x.fields.updated, reverse=True)
  
  bitbar_header.append("%s" % ("---"))
  recent = 'Recent(' + str(TOPRECENT) + '):'
  bitbar_header.append("%s" % (recent))

  ###############################################################################
  ## TOP RECENT
  ####################
  i = 0
  for element in myIssues:
    status=""
    sprintName = ''
    if(element.fields.customfield_10007):
      fieldIndex = 0
      if(len(element.fields.customfield_10007) > 1):
        fieldIndex = 1
      try:
        sprintName = element.raw['fields']["customfield_10007"][0]['name']
      except AttributeError:
        sprintName = ''

    # Create ticket with sprint name if it exsist
    # <ID>(<status>) :: <Title>
    issue_status = str(element.fields.status)
    issue_status = issue_status.replace("&", "and")
    status = status + str(element.key) + "(" + issue_status + ") :: " + str(element.fields.summary)
    if(len(status) > TICKETLENGTH):
      status = status[0:TICKETLENGTH] + '..'
    else:
      status = status[0:TICKETLENGTH]

    status = status + " | href=" + SERVER + "/browse/" + str(element.key)

    # adding ticket to sprint
    if(sprintName):
      status = sprintName + " # " + status
      mySprints[sprintName].append("%s" % (status))
    else:
      mySprints[NONSPRINT].append("%s" % (status))

    # just show top TOPRECENT tickets
    if(i < TOPRECENT):
      bitbar_header.append("%s" % (status))

    if (issue_status not in ('Open', 'Prepare Testing')):
      top_status_bar = str(element.key) + "(" + issue_status + ") :: " + str(element.fields.summary)
      if(len(top_status_bar) > STATUSLENGTH):
        top_status_bar = top_status_bar[0:STATUSLENGTH] + '..'

      ###############################################################################
      ## header element
      ####################
      if(bitbar_header[0] == ''):
        bitbar_header[0] = str("%s" % (top_status_bar))
        ## link to that elem
        bitbar_header[2] = str("%s" % (status))
      ###############################################################################

    i = i + 1  
  
  if(bitbar_header[0] == ''):
    bitbar_header[0] = '(-) :: No "In progress" ticket'


  ###############################################################################
  content = '\n'.join(bitbar_header)
  # print(content)
  
  with open(CACHE_FILE, "w+") as f:
    f.write(content)
    f.write("\n---\n")
    f.write("cached\n")
    f.write(time.ctime())
    f.close()

  return (content)


def getParsedIssues():
  log = logging.getLogger(__name__)

  parseConfigFile()

  if(USER == "example@example.com" or PASSW == "dummypassword"):
    return "Missing Credentials for JIRA! Please update the config file! Restart after edit!"
  jira = connect_jira(log, SERVER, USER, PASSW)
  log = ""
  if ( jira is not None):
    issues = jira.search_issues(QUERY)
    if(len(issues) > 0):
      log = get_in_progress_item(issues)
    else:
      bitbar_header = ['No jira issue', '---', 'Connection error?']
      log = ('\n'.join(bitbar_header))

  return log
