import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task, TaskType, Scheduler, Owner


def test_mark_complete_changes_status():
    task = Task(
        name="Morning Walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=5,
    )

    assert task.is_completed is False   # starts incomplete
    task.mark_complete()
    assert task.is_completed is True    # now complete


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(
        name="Breakfast",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=5,
    )

    assert len(pet.get_tasks()) == 0    # no tasks yet
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1    # task was added
