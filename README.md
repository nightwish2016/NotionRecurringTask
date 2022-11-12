# Requirements

1.  Recurring tasks

| Requirement                                                  |
| ------------------------------------------------------------ |
| Create template page for  recurring tasks and  create recurring tasks in this template page |
| Query recurring tasks  in template page, Create different recurring tasks by different recurring task types,For example, Homework review is workday task , Nucleic acid testing is weekly taskk, and some tasks only occurs on specific days(Monday,Thursday etc) |


2.  Automatically update task status

| Requirement                                                  |
| ------------------------------------------------------------ |
| Task is already  expired ,We need to complete this task ASAP,So mark this task as **Doing** Status to complete this task today |
| If task will be expired in X days(X shouldn't be empty or 0),We'd better to mark task status as **Todo** to avoid forgetting  to complete this task |
| If task will be expired today,Mark task as **Doing** status  |
| If task expiration date is within date range,Mark task as Doing status |
| If you forgot to input expiration date for your task yesterday , Update task expirationDate to the date of **yesterday**,Mark task status as **Todo** |
| If task is completed(Task status is Done),Update **CompletedDate** to the date of **yesterday**,This task will not show  in your daily task board |

# Solution and Design

## Diagram 

1. #### Recurring tasks creation 

   ![](http://kevinbucket2020.oss-cn-hangzhou.aliyuncs.com/HexoBlog/RecurringTaskCreation/RecurringTaskCreation.png)

2. #### Automatically Update daily tasks

   ![](http://kevinbucket2020.oss-cn-hangzhou.aliyuncs.com/HexoBlog/RecurringTaskCreation/TaskStatusUpdate.png)



# Solutions

1. Run this python package in Jenkins,see details in page http://nightwish.tech/2022/10/01/DailyTaskCreationByJenkins/
2. Call this python package  by Azure function timer trigger [English](https://nightwish.tech/2022/11/25/RecurringTaskCreationEnglish/#more)，[中文](https://nightwish.tech/2022/09/25/RecurringTaskCreation/)
3. Call this python package by Windows task scheduler   http://nightwish.tech/2022/10/01/DailyTaskCreationByTaskSechduler/

# Package Installation

## Python Package

https://test.pypi.org/project/NotionRecurringTask-KevinZhou/

Install package : pip install -i https://test.pypi.org/simple/NotionRecurringTask-KevinZhou

# Notion API reference

https://developers.notion.com/docs/getting-started

