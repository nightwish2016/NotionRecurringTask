from NotionRecurringTask.RecurringTask import RecurringTask
from dotenv import load_dotenv
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

if __name__ == "__main__":
    required_variables = (
        "AUTH",
        "DATABASE_TEMPLATE_ID",
        "DATABASE_ID",
        "OFF_DATABASE_ID",
    )
    missing_variables = [name for name in required_variables if not os.getenv(name)]
    if missing_variables:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing_variables)}"
        )

    auth = os.environ["AUTH"]
    task_configuration_database_id = os.environ["DATABASE_TEMPLATE_ID"]
    database_id = os.environ["DATABASE_ID"]
    off_day_database_id = os.environ["OFF_DATABASE_ID"]
    time_delta_with_utc = 8
    notion = RecurringTask()
    notion.process(
        auth,
        task_configuration_database_id,
        off_day_database_id,
        database_id,
        time_delta_with_utc,
    )