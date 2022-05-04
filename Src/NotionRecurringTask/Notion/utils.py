from asyncio import Task
import json
import os,sys
from datetime import datetime,timedelta, date
import datetime as dt
from pathlib import Path
from NotionRecurringTask.Notion.TaskConfiguration import TaskConfiguration
from NotionRecurringTask.notion import *

import logging
logging.basicConfig(encoding='utf-8', level=logging.INFO)
class Utils:
    def __init__(self): 
        self.__baseurl="https://api.notion.com" 
        self.__auth="secret_Y6RG2tlin3I8fIK5G4LDioYFqiZYS4oPfCBuc0K75vG"
        self.client=NotionAPIClient(self.__baseurl,self.__auth)   
        pass
    def createDailyTask(self,taskConfiguration_dabaseid,databaseid):
    #    task_ls=self.getDailyTaskFromFile()
        task_ls=self.getTaskConfiguration(taskConfiguration_dabaseid)
        utc_timestamp = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) 
        now_utc8=(utc_timestamp+dt.timedelta(hours=8))
        # print("utc now"+str(utc_timestamp) )       
        # print("utc8 now"+str(now_utc8) )
        for task in task_ls:
            endDate = datetime.strptime(task.EndDate, '%Y-%m-%d')  
            if now_utc8.date()<=endDate.date():                           
                if task.Type=="Daily"  :
                    self.createTask(databaseid,task)
                elif task.Type=="Workday":                                          
                    if now_utc8.weekday()<5: #workday
                        self.createTask(databaseid,task)
                elif task.Type=="SpecificDay":       
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    if days[now_utc8.weekday()] in task.CycleDays: #workday
                        self.createTask(databaseid,task)
                elif task.Type=="SpecificDateRange": 
                    dateRange=task.CycleDateRange                        
                    startDate=datetime.strptime(dateRange[0], '%Y-%m-%d')   
                    endDate= datetime.strptime(dateRange[1], '%Y-%m-%d')   
                    if now_utc8.date()>=startDate.date() and now_utc8.date()<=endDate.date(): #workday
                        self.createTask(databaseid,task)
                else:
                    pass

    
    def getDailyTaskFromFile(self):
        path=os.path.join(Path(__file__).parent.parent.absolute(),"data.json")
        taskJson=""
        with open(path, "r",encoding="utf8") as fa:
            taskJson = fa.read()
        task_list=json.loads(taskJson,object_hook=JSONObject)
        return task_list

    def getTaskWithTBDStatusAndExpirationDateIsNotEmpty(self,databaseid):
        client=self.client
        body="""
        {
    "filter":{
    "and":[{
        "property": "Status",
        "select": {
            "equals": "TBD"
        }
    },
    {
        "property": "ExpirationDate/DateRange",
        "date": {
            "is_not_empty": true
        }
    }
    ]    
    }
}
        """   
        data=json.loads(body)	
        s=client.send_post("databases/{0}/query".format(databaseid),data) #read all data from databases        
        # print(s)
        return s

    def updateTaskStatus(self,pageid,status):
        client=self.client
        body="""
        {"properties": {
 "Status" :{
                "select": {
                    "name": "To Do"
                }
            }
}
}
        """
        data=json.loads(body)	
        data["properties"]["Status"]['select']['name']=status
        s=client.send_patch("pages/{0}".format(pageid),data) #read all data from databases
        # print(s)

    def updateTaskWithTBDStatusToSpecificStatus(self,databaseid,day):   
        pagels=self.getTaskWithTBDStatusAndExpirationDateIsNotEmpty(databaseid)
        pagelist=pagels["results"]
        for page in pagelist:
            pageid=page["id"]            
            expirationDateStr=""            
            taskName=page["properties"]["Name"]["title"][0]["text"]['content']
            startDateStr=page["properties"]['ExpirationDate/DateRange']["date"]["start"]
            endDateStr=page["properties"]['ExpirationDate/DateRange']["date"]["end"]
            if endDateStr is  not None:  
                expirationDateStr=endDateStr
            else:
                expirationDateStr=startDateStr            
            startDate=datetime.strptime(startDateStr, '%Y-%m-%d')      
            expirationDate = datetime.strptime(expirationDateStr, '%Y-%m-%d')        
            utc_timestamp = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) 
            now_utc8=utc_timestamp+dt.timedelta(hours=8)    
            if endDateStr is None:                # The value is not dateRage,it's expirationDate
                if (now_utc8+timedelta(days=day)).date()>=expirationDate.date():  #Task will be expired in XX days
                    logging.info("Task [{0}] will be expired on {1},update Status to \"To Do\"".format(taskName,expirationDate.date()))
                    self.updateTaskStatus(pageid,"To Do") 
            else: #dateRange
                if  now_utc8.date()>=startDate.date() and now_utc8.date()<=expirationDate.date():
                    logging.info("Task [{0}] should  be in progress between {1}  and {2},update Status to \"Doing\"".format(taskName,startDate.date(),expirationDate.date()))
                    self.updateTaskStatus(pageid,"Doing") 

            if now_utc8.date()>=expirationDate.date():   #Already expired
                logging.info("Task:[{0}] is already expired on {1},update Status to \"doing\"".format(taskName,expirationDate.date()))
                self.updateTaskStatus(pageid,"Doing")                                   
             
    def createTask(self,databaseid,task):
        logging.info("Daily task creating:[{0}]".format(task.Title))       
        client=self.client   		
        body="""
    {"parent": {
            "database_id": "databaseid"
        },
        "properties": {
            "title": {
                "title": [{
                    "type": "text",
                    "text": {
                        "content": "aaa"
                    }
                }]
            },
            "Status" :{
                "select": {
                    "name": "Doing"
                }
            }
        },
        "children": [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": "123"
                    }
                }]
            }
        }]
    }"""
        data=json.loads(body)
        data["properties"]["title"]["title"][0]["text"]['content']=task.Title
        data["properties"]["Status"]['select']['name']=task.Status
        data["parent"]["database_id"]=databaseid
        data["children"][0]["paragraph"]['rich_text'][0]['text']['content']=""
        result=client.send_post("pages",data)
        logging.info("Daily task created:[{0}] ".format(task.Title))       

    def getTaskConfigurationFromNotion(self,databaseid):        
        client=self.client
        body="""
        {
    "filter":{
    "and":[{
        "property": "Status",
        "select": {
            "does_not_equal": "Invalid"
        }
    }
    ]
    }
}
        """   
        data=json.loads(body)	
        s=client.send_post("databases/{0}/query".format(databaseid),data) #read all data from databases        
        # print(s)
        return s
    def getTaskConfiguration(self,databaseid):
        notionResult=self.getTaskConfigurationFromNotion(databaseid)
        notionConfiguration_list=[]        
        if len(notionResult)>0:            
            notionResultList=notionResult["results"]
            for notionResult in notionResultList:
                configuration=TaskConfiguration()
                configuration.Title=notionResult["properties"]["Title"]['title'][0]["text"]['content']
                configuration.Type=notionResult["properties"]['Type']['select']['name']
                configuration.EndDate=notionResult["properties"]['EndDate']['date']['start']
                configuration.Status=notionResult["properties"]['Status']['select']['name']
               
                days=notionResult["properties"]['Cycle Days']['multi_select'] 
                day_ls=[]   
                if len(days)>0:     
                    for day in days:
                        day_ls.append(day["name"])
                configuration.CycleDays=day_ls 

                cycleDateRange=notionResult["properties"]['Cycle Date']['date']
                cycleDate=[]
                if cycleDateRange is not None:
                    startDateStr=cycleDateRange['start']
                    endDateStr=cycleDateRange['end']                
                    cycleDate.append(startDateStr)
                    cycleDate.append(endDateStr)
                configuration.CycleDateRange=cycleDate

                notionConfiguration_list.append(configuration)    
        return  notionConfiguration_list         
        
class JSONObject:
    def __init__(self, d):
        self.__dict__ = d  