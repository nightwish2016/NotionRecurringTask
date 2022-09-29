# Requirements

1. Recurring tasks

   | Requirement                                                  | Comment |
   | ------------------------------------------------------------ | ------- |
   | Create a recurring task tempalate page and Create your recurring task(Daily task,Working day task,Weekly task etc) |         |
   | Automatically create daily task by recurring task template page |         |

2. Other tasks

   | Requirement                                                  | Comment                                                      |
   | ------------------------------------------------------------ | ------------------------------------------------------------ |
   | When  task is in TBD/Empty status and task expiration Date is less than today,Then mark task as Doing status | This task is already expired or will be expired today, We have to do it from today ,So we need to mark this task as Doing status |
   | When Task is in TBD/Empty status and task will be expired within 3 days, Then mark task as Todo status | As task will be expired within 3 days, We have complete the tasks as soon as possible,So we need to mark this task as ToDo status in case we forget to complete this task. If you would like to complete this task today, You could put this task in Doing group. |
   | When task is in TBD/Empty status and today is within the date range ,Then mark task as  Doing satus | We should get started for this task  as today is within the date range. For example , Today is 9/24/2022 and DateRange is 9/24/2022-9/30/2022 |
   | When task exipiration date is empty ,  Then update task expiration Date to Today | When you create a task ,But you  forget to fill  expiration date, we need to complete this task today by default |
   | When Task is in Done Status, Then ExpirationDate will be populated | When completedDate<Today and task status is Done,  Daily task dash board will  not contain the task that already have completed yeserday |

# **Recurring task template page introduction**

![RecurringTask](http://kevinbucket2020.oss-cn-hangzhou.aliyuncs.com/HexoBlog/Notion/Create%20Daily%20task%20By%20template/RecurringTask.png)

| Column     | Value                                 | Comment                                                   |
| ---------- | ------------------------------------- | --------------------------------------------------------- |
| Title      | task name                             | task name                                                 |
| Status     | TBD,Todo,Doing,Done,Blocker，Invalid  | Task status                                               |
| Type       | WorkDay,SpecificDay,SpecificDateRange | Recurring task type                                       |
| Tag        | Work,Life,Python,Docker etc           | Tag to distinguish  tasks                                 |
| Cycle Date | 9/18/2022-9/25/2022                   | Recurring task will be created within  date range         |
| Cycle Days | From Monday to Sunday                 | you could choose multiple days                            |
| EndDate    | Task's  end date                      | Recuring task will not be created if task's endDate<Today |

 **Task status**

| Task Status           | Comment                                                      |
| --------------------- | ------------------------------------------------------------ |
| TBD(To be determined) | Task will be started in the future, But we already don't   know when it will get started. It similar with the stories that in Backlog of Jira |
| Todo                  | The task that we will start do it today                      |
| Doing                 | The task that we are doing today                             |
| Done                  | The task that we already completed it.                       |
| Blocker               | The task have dependency  , We can't start task until task dependency is removed |
| Invalid               | Invalid Task is only used in recurring task template page    |

# Installation

## Python Package

https://test.pypi.org/project/NotionRecurringTask-KevinZhou/

Install package : pip install -i https://test.pypi.org/simple/NotionRecurringTask-KevinZhou



# How to use this python package to  create daily tasks

### Prerequisite

1. Create a task template page  in Notion for recurring tasks, see sample as below, Please duplicate this page if you are interested

 https://stone-fighter-9fa.notion.site/530ba8c6780d4f668235e9b62f697d92?v=c802b9ed6928482c88da55051b41bb32  
![RecurringTask](http://kevinbucket2020.oss-cn-hangzhou.aliyuncs.com/HexoBlog/Notion/Create%20Daily%20task%20By%20template/RecurringTask.png)

​	2. Create Daily task page in Notion，see details in https://stone-fighter-9fa.notion.site/DailyTask-Demo-59a57f31d29b4dfcab5db9d20aeca6ab, you also could duplicate this page and update configurations for your daily task dashboard



### Code sample to call this python package by Azure function TimerTrigger



```python
import datetime
import logging
import os
import azure.functions as func
from NotionRecurringTask.RecurringTask import RecurringTask

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
    auth=os.environ["Auth"]
    taskConfiguration_dabaseid=os.environ["TaskConfiguration_dabaseid"]
    timeDeltaWithUTC=(int)(os.environ["TimeDeltaWithUTC"])
    databaseid=os.environ["DatabaseID"]
    knotion=RecurringTask()  
    knotion.process(auth,taskConfiguration_dabaseid,databaseid,timeDeltaWithUTC)
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
```

### Test,See details in my blog: http://nightwish.tech

# Another solutions to create daily notion tasks

1. reate jenkins job to call this package to create recurring task (TBD)


2. Create job in windows task sechdualers to call this package to create recurring  task(TBD)

# Notion API reference

https://developers.notion.com/docs/getting-started

