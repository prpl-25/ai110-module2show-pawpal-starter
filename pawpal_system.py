from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskType(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"


# ---------------------------------------------------------------------------
# Dataclasses  (pure data, no business logic)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    task_type: TaskType
    duration_minutes: int
    priority: int                        # 1 (low) – 5 (high)
    preferred_time: Optional[str] = None # e.g. "08:00"
    is_completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ScheduledTask:
    task: Task
    start_time: str   # "HH:MM"
    end_time: str     # "HH:MM"


@dataclass
class MedicalRecord:
    pet_id: str
    condition: str = ""
    medications: list[str] = field(default_factory=list)
    vet_notes: str = ""
    last_checkup: Optional[date] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_medication(self, med: str) -> None:
        pass  # TODO

    def remove_medication(self, med: str) -> None:
        pass  # TODO


@dataclass
class FeedingSchedule:
    pet_id: str
    meals_per_day: int = 2
    food_type: str = ""
    portion_size: float = 0.0            # in grams / cups (owner's choice)
    feeding_times: list[str] = field(default_factory=list)  # ["08:00", "18:00"]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def generate_feeding_tasks(self) -> list[Task]:
        """Return one Task per scheduled feeding time."""
        pass  # TODO


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0
    weight: float = 0.0
    owner_id: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _tasks: list[Task] = field(default_factory=list, repr=False)

    def add_task(self, task: Task) -> None:
        pass  # TODO

    def remove_task(self, task_id: str) -> None:
        pass  # TODO

    def get_tasks(self) -> list[Task]:
        pass  # TODO


@dataclass
class Owner:
    name: str
    email: str = ""
    time_available_minutes: int = 60
    preferences: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _pets: list[Pet] = field(default_factory=list, repr=False)

    def add_pet(self, pet: Pet) -> None:
        pass  # TODO

    def remove_pet(self, pet_id: str) -> None:
        pass  # TODO

    def get_pets(self) -> list[Pet]:
        pass  # TODO


@dataclass
class DailyPlan:
    pet_id: str
    date: date
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    total_time_minutes: int = 0
    reasoning: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_task(self, task: ScheduledTask) -> None:
        pass  # TODO

    def remove_task(self, task_id: str) -> None:
        pass  # TODO

    def get_summary(self) -> str:
        pass  # TODO


# ---------------------------------------------------------------------------
# Scheduler  (business logic lives here)
# ---------------------------------------------------------------------------

class Scheduler:
    """Generates a DailyPlan for a pet given the owner's available time."""

    def generate_plan(self, pet: Pet, available_time: int) -> DailyPlan:
        """Build and return a DailyPlan."""
        pass  # TODO

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by priority (descending)."""
        pass  # TODO

    def fit_tasks(self, tasks: list[Task], time_limit: int) -> list[Task]:
        """Return the subset of tasks that fit within time_limit minutes."""
        pass  # TODO

    def explain_reasoning(self, plan: DailyPlan) -> str:
        """Return a human-readable explanation of why the plan was built this way."""
        pass  # TODO
