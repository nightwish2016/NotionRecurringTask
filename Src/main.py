from NotionRecurringTask.RecurringTask import RecurringTask

if __name__ == "__main__":
    auth="XXX"
    taskConfiguration_dabaseid='XXXXX'
    databaseid='XXX'
    offDayDatabaseId='XXX'
    timeDeltaWithUTC=8
    knotion=RecurringTask()    
    knotion.process(auth,taskConfiguration_dabaseid,offDayDatabaseId,databaseid,timeDeltaWithUTC)