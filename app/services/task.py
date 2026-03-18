from sqlalchemy.orm import Session

from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class TaskService:
    """Ключевые операции с задачами, включая бизнес-логику, валидацию и прочее"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = TaskRepository(db)

    def list_tasks(self) -> list[TaskRead]:
        tasks = self.repository.get_all()
        return [TaskRead.model_validate(task) for task in tasks]

    def create_task(self, payload: TaskCreate) -> TaskRead:
        task = self.repository.create(title=payload.title)
        self.db.commit()
        self.db.refresh(task)
        return TaskRead.model_validate(task)

    def update_task(self, task_id: str, payload: TaskUpdate) -> TaskRead:
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError

        if payload.title is not None:
            task.title = payload.title
        if payload.completed is not None:
            task.completed = payload.completed

        self.db.commit()
        self.db.refresh(task)
        return TaskRead.model_validate(task)

    def delete_task(self, task_id: str) -> None:
        task = self.repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError

        self.repository.delete(task)
        self.db.commit()
