
from ..app.repositories.task_repository import (create_task)
from ..database.session import (get_session)
from ..app.api.api_schema import (TaskRequest)
from ..database import (Task)

session=get_session()
async def create_dev_task():
  task = Task(
    "dev_id"
  )