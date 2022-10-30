from NotionRecurringTask.Notion.utils import *
import argparse
import logging 

class RecurringTask:
    def __init__(self):       
        pass
    def process(self,auth,taskConfiguration_dabaseid,databaseid,deltaTimeWithUTC):            
        u=Utils(auth,deltaTimeWithUTC)		
        days=0
        u.createDailyTask(taskConfiguration_dabaseid,databaseid)
        u.UpdateTaskStatus(databaseid,days)

    
        
    
