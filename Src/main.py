from NotionRecurringTask.RecurringTask import RecurringTask
from dotenv import load_dotenv
import os
load_dotenv()

if __name__ == "__main__":
    auth=os.getenv('AUTH')
    taskConfiguration_dabaseid=os.getenv('DATABASE_TEMPLATE_ID')
    databaseid=os.getenv('DATABASE_ID')
    offDayDatabaseId=os.getenv('OFF_DATABASE_ID')
    timeDeltaWithUTC=8
    knotion=RecurringTask()    
    knotion.process(auth,taskConfiguration_dabaseid,offDayDatabaseId,databaseid,timeDeltaWithUTC)