from NotionRecurringTask.Notion.utils import *
import argparse
import logging 

class RecurringTask:
    def __init__(self):       
        pass
    def process(self,auth,taskConfiguration_dabaseid,databaseid,deltaTimeWithUTC):            
        u=Utils(auth,deltaTimeWithUTC)		
        u.createDailyTask(taskConfiguration_dabaseid,databaseid)
        u.autoFillCompleteDate(databaseid)        
        days=3
        u.updateTaskWithTBDOrEmptyStatusToSpecificStatus(databaseid,days)
        u.UpdateEmptyExpirationTask(databaseid)
      





    # if __name__ == "__main__": 
    #     databaseid='6fde392034f34834ad6ca952b57a1d1a'
    #     process(databaseid)
        
    
