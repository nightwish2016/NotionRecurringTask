from NotionRecurringTask.Notion.utils import *
import argparse
import logging 

class RecurringTask:
    def __init__(self):       
        pass
    def process(self,taskConfiguration_dabaseid,databaseid):      
        u=Utils()		
        u.createDailyTask(taskConfiguration_dabaseid,databaseid)
        days=3
        u.updateTaskWithTBDStatusToSpecificStatus(databaseid,days)
      





    # if __name__ == "__main__": 
    #     databaseid='6fde392034f34834ad6ca952b57a1d1a'
    #     process(databaseid)
        
    
