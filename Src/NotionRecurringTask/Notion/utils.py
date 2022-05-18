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
    def __init__(self,auth,deltaTime): 
        self.__baseurl="https://api.notion.com" 
        self.__auth=auth
        self.client=NotionAPIClient(self.__baseurl,self.__auth)
        self.deltaTime=deltaTime   
        pass
    def createDailyTask(self,taskConfiguration_dabaseid,databaseid):
    #    task_ls=self.getDailyTaskFromFile()
        task_ls=self.getTaskConfiguration(taskConfiguration_dabaseid)
        utc_timestamp = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) 
        now_utc8=(utc_timestamp+dt.timedelta(hours=self.deltaTime))
        # print("utc now"+str(utc_timestamp) )       
        # print("utc8 now"+str(now_utc8) )
        for task in task_ls:                        
            endDate = datetime.strptime(task.EndDate, '%Y-%m-%d')  
            if now_utc8.date()<=endDate.date():                           
                if task.Type=="Daily":
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

    def autoFillCompleteDate(self,databaseid):
        notion_Result=self.getTaskWithDoneStatusAndEmptyCompleteDate(databaseid)
        results=notion_Result['results']
        utc_timestamp = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) 
        now_utc8=utc_timestamp+dt.timedelta(hours=self.deltaTime)  
        lastDate=now_utc8+dt.timedelta(days=-1) 
        for result in results:
            completeDate=result['properties']['CompleteDate']['date']
            pageid=result["id"] 
            taskName=result['properties']["Name"]["title"][0]["text"]['content']            
            if completeDate is None:
                #update completeDate
                logging.info("Fill Completed task [{0}] with date {1}".format(taskName,str(lastDate.date())))
                self.updateTaskCompleteDate(pageid,str(lastDate.date()))       


    def getDailyTaskFromFile(self):
        path=os.path.join(Path(__file__).parent.parent.absolute(),"data.json")
        taskJson=""
        with open(path, "r",encoding="utf8") as fa:
            taskJson = fa.read()
        task_list=json.loads(taskJson,object_hook=JSONObject)
        return task_list

    def getTaskWithTBDOrEmptyStatusAndExpirationDateIsNotEmpty(self,databaseid):
        client=self.client
        body="""
        {
     "filter": {
         "and": [{
                 "or": [{
                         "property": "Status",
                         "select": {
                             "equals": "TBD"
                         }
                     },
                     {
                         "property": "Status",
                         "select": {
                             "is_empty": true
                         }
                     }

                 ]
             },
             {
                 "property": "ExpirationDate/DateRange",
                 "date": {
                     "is_not_empty": true
                 }
             },
             {
                 "property": "CompleteDate",
                 "date": {
                     "is_empty": true
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
    

    def getTaskWithEmptyExpirationDate(self,databaseid):
        client=self.client
        body="""
        {
     "filter": {
         "and": [{
                 "or": [{
                         "property": "Status",
                         "select": {
                             "equals": "TBD"
                         }
                     },
                     {
                         "property": "Status",
                         "select": {
                             "is_empty": true
                         }
                     }

                 ]
             },
             {
                 "property": "ExpirationDate/DateRange",
                 "date": {
                     "is_empty": true
                 }
             },
              {
                 "property": "CompleteDate",
                 "date": {
                    "is_empty": true
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
    
    def updateTask(self,pageid,status,expirationDate):
        client=self.client
        body="""
        {"properties": {
 "Status" :{
                "select": {
                    "name": "To Do"
                }
            },
             "ExpirationDate/DateRange" : {
                "date": {
                "start": "2021-04-26"       
                }
            }
}
}
        """
        data=json.loads(body)	
        data["properties"]["Status"]['select']['name']=status
        data["properties"]['ExpirationDate/DateRange']['date']['start']=expirationDate
        s=client.send_patch("pages/{0}".format(pageid),data) #read all data from databases
        # print(s)

    
    def updateTaskCompleteDate(self,pageid,completeDate):
        client=self.client
        body="""
            {"properties": {       
                    "CompleteDate" : {
                    "date": {
                    "start": "2021-04-26"       
                    }
                }
        }
        }
        """
        data=json.loads(body)	
        data["properties"]['CompleteDate']['date']['start']=completeDate
        s=client.send_patch("pages/{0}".format(pageid),data) #read all data from databases
        # print(s)

    def UpdateEmptyExpirationTask(self,databaseid):
        pagels_emptyExpirationDate=self.getTaskWithEmptyExpirationDate(databaseid)     
        pagelist__emptyExpirationDate=pagels_emptyExpirationDate["results"]
        utc_timestamp = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) 
        now_utc8=utc_timestamp+dt.timedelta(hours=self.deltaTime)          
        for page in pagelist__emptyExpirationDate:
            pageid=page["id"]  
            taskName=""
            if len(page["properties"]["Name"]["title"])>0:           
                taskName=page["properties"]["Name"]["title"][0]["text"]['content']
            date=page["properties"]['ExpirationDate/DateRange']["date"]
            if date is None:
                logging.info("Task [{0}] expirationDate is None,Update status to [To Do],update ExpirationDate to Today".format(taskName))
                self.updateTask(pageid,"To Do",str(now_utc8.date())) 

    def updateTaskWithTBDOrEmptyStatusToSpecificStatus(self,databaseid,day):   
        pagels=self.getTaskWithTBDOrEmptyStatusAndExpirationDateIsNotEmpty(databaseid)     
        pagelist=pagels["results"]               
        for page in pagelist:
            pageid=page["id"]            
            expirationDateStr=""
            taskName=""
            if len(page["properties"]["Name"]["title"])>0:           
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
            now_utc8=utc_timestamp+dt.timedelta(hours=self.deltaTime)    
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
            },
            "Tag" :{
                "multi_select": [{
                    "name": "Work"
                }]
            },
            "ExpirationDate/DateRange" : {
                "date": {
                "start": "2021-04-26"       
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
        utc_timestamp = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc) 
        now_utc8=utc_timestamp+dt.timedelta(hours=self.deltaTime)    
        data=json.loads(body)
        data["properties"]["title"]["title"][0]["text"]['content']=task.Title
        data["properties"]["Status"]['select']['name']=task.Status
        data["properties"]["Tag"]['multi_select']=task.Tag
        data["properties"]['ExpirationDate/DateRange']['date']['start']=str(now_utc8.date())
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


                tags=notionResult["properties"]['Tag']['multi_select'] 
                tag_ls=[]   
                if len(tags)>0:     
                    for tag in tags:
                        tag_ls.append({"name":tag["name"]})
                configuration.Tag=tag_ls

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


    def getTaskWithDoneStatusAndEmptyCompleteDate(self,databaseid):        
        client=self.client
        body="""
                {
 	"filter": {
 		"and": [{
 				"property": "Status",
 				"select": {
 					"equals": "Done"
 				}
 			},
 			{
 				"property": "CompleteDate",
 				"date": {
 					"is_empty": true
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

        
class JSONObject:
    def __init__(self, d):
        self.__dict__ = d  