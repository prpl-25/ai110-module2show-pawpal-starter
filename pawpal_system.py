from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
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
# Task
# Represents a single pet care activity with duration, priority, and status.
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    task_type: TaskType
    duration_minutes: int
    priority: int                        # 1 (low) – 5 (high)
    preferred_time: Optional[str] = None # "HH:MM", e.g. "08:00"
    is_completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_complete(self) -> None:
        self.is_completed = True

    def mark_incomplete(self) -> None:
        self.is_completed = False

    def recur(self) -> "Task":
        """Return a fresh copy of this task reset to incomplete (for daily recurrence)."""
        return Task(
            name=self.name,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
        )

    def __str__(self) -> str:
        status = "✓" if self.is_completed else "○"
        time_hint = f" @ {self.preferred_time}" if self.preferred_time else ""
        return (
            f"[{status}] {self.name} ({self.task_type.value}) "
            f"— {self.duration_minutes} min, priority {self.priority}{time_hint}"
        )


# ---------------------------------------------------------------------------
# ScheduledTask
# Wraps a Task with a concrete start/end time inside a DailyPlan.
# ---------------------------------------------------------------------------

@dataclass
class ScheduledTask:
    task: Task
    start_time: str   # "HH:MM"
    end_time: str     # "HH:MM"

    def __str__(self) -> str:
        return f"{self.start_time}–{self.end_time}  {self.task.name}"


# ---------------------------------------------------------------------------
# MedicalRecord
# ---------------------------------------------------------------------------

@dataclass
class MedicalRecord:
    pet_id: str
    condition: str = ""
    medications: list[str] = field(default_factory=list)
    vet_notes: str = ""
    last_checkup: Optional[date] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_medication(self, med: str) -> None:
        if med not in self.medications:
            self.medications.append(med)

    def remove_medication(self, med: str) -> None:
        self.medications = [m for m in self.medications if m != med]


# ---------------------------------------------------------------------------
# FeedingSchedule
# ---------------------------------------------------------------------------

@dataclass
class FeedingSchedule:
    pet_id: str
    meals_per_day: int = 2
    food_type: str = ""
    portion_size: float = 0.0
    feeding_times: list[str] = field(default_factory=list)  # ["08:00", "18:00"]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def generate_feeding_tasks(self) -> list[Task]:
        """Return one high-priority Task per scheduled feeding time."""
        tasks = []
        for t in self.feeding_times:
            tasks.append(Task(
                name=f"Feed ({self.food_type or 'meal'})",
                task_type=TaskType.FEEDING,
                duration_minutes=10,
                priority=5,
                preferred_time=t,
            ))
        return tasks


# ---------------------------------------------------------------------------
# Pet
# Stores pet details and owns a list of Tasks.
# ---------------------------------------------------------------------------

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

    # --- task management ---------------------------------------------------

    def add_task(self, task: Task) -> None:
        """Add a task; ignore duplicates (same id)."""
        if not any(t.id == task.id for t in self._tasks):
            self._tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove task by id; silently ignores unknown ids."""
        self._tasks = [t for t in self._tasks if t.id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return a copy of the task list."""
        return list(self._tasks)

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self._tasks if not t.is_completed]

    def get_tasks_by_type(self, task_type: TaskType) -> list[Task]:
        return [t for t in self._tasks if t.task_type == task_type]

    def get_tasks_filtered(
        self,
        task_type: Optional[TaskType] = None,
        min_priority: int = 1,
        pending_only: bool = False,
    ) -> list[Task]:
        """Return tasks matching all filters, sorted by priority desc then duration asc."""
        tasks = self._tasks
        if pending_only:
            tasks = [t for t in tasks if not t.is_completed]
        if task_type is not None:
            tasks = [t for t in tasks if t.task_type == task_type]
        tasks = [t for t in tasks if t.priority >= min_priority]
        return sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))

    # --- display -----------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self.name} ({self.species}"
            + (f", {self.breed}" if self.breed else "")
            + f") — age {self.age}, {len(self._tasks)} task(s)"
        )


# ---------------------------------------------------------------------------
# Owner
# Manages multiple pets and provides a unified view across all their tasks.
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    email: str = ""
    time_available_minutes: int = 60
    preferences: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _pets: list[Pet] = field(default_factory=list, repr=False)

    # --- pet management ----------------------------------------------------

    def add_pet(self, pet: Pet) -> None:
        """Add a pet and stamp its owner_id."""
        if not any(p.id == pet.id for p in self._pets):
            pet.owner_id = self.id
            self._pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        self._pets = [p for p in self._pets if p.id != pet_id]

    def get_pets(self) -> list[Pet]:
        return list(self._pets)

    def get_pet_by_name(self, name: str) -> Optional[Pet]:
        for pet in self._pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    # --- cross-pet task views ----------------------------------------------

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every (pet, task) pair across all pets."""
        return [(pet, task) for pet in self._pets for task in pet.get_tasks()]

    def get_all_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return pending (pet, task) pairs across all pets."""
        return [(pet, task) for pet in self._pets for task in pet.get_pending_tasks()]

    def __str__(self) -> str:
        return (
            f"Owner: {self.name} | {len(self._pets)} pet(s) "
            f"| {self.time_available_minutes} min available"
        )


# ---------------------------------------------------------------------------
# DailyPlan
# ---------------------------------------------------------------------------

@dataclass
class DailyPlan:
    pet_id: str
    date: date
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    total_time_minutes: int = 0
    reasoning: str = ""
    conflicts: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_task(self, scheduled: ScheduledTask) -> None:
        self.scheduled_tasks.append(scheduled)
        self.total_time_minutes += scheduled.task.duration_minutes

    def remove_task(self, task_id: str) -> None:
        removed = [st for st in self.scheduled_tasks if st.task.id == task_id]
        for st in removed:
            self.total_time_minutes -= st.task.duration_minutes
        self.scheduled_tasks = [st for st in self.scheduled_tasks if st.task.id != task_id]

    def get_summary(self) -> str:
        if not self.scheduled_tasks:
            return f"No tasks scheduled for {self.date}."
        lines = [f"Daily Plan — {self.date}  ({self.total_time_minutes} min total)\n"]
        for st in self.scheduled_tasks:
            lines.append(f"  {st}")
        if self.reasoning:
            lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler
# The "brain": retrieves, organises, and schedules tasks across a pet's day.
# ---------------------------------------------------------------------------

class Scheduler:
    """
    Builds a DailyPlan for a single pet.

    Scheduling rules (in order):
      1. Incomplete tasks only.
      2. Sort by priority descending; break ties by duration ascending
         (shorter high-priority tasks first so we fit more in).
      3. Greedily add tasks until available_time is exhausted.
      4. Respect preferred_time if given; otherwise assign sequentially
         starting from START_HOUR.
    """

    START_HOUR: str = "08:00"   # default day start

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority desc, then duration asc (greedy-friendly)."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by preferred_time (HH:MM) ascending; tasks without a time go last."""
        return sorted(
            tasks,
            key=lambda t: t.preferred_time if t.preferred_time else "99:99",
        )

    def filter_tasks(
        self,
        tasks: list[Task],
        pending_only: bool = False,
        pet_name: str | None = None,
        pet: "Pet | None" = None,
    ) -> list[Task]:
        """Filter tasks by completion status and/or owning pet.

        Args:
            tasks:       The task list to filter.
            pending_only: When True, keep only incomplete tasks.
            pet_name:    When given, keep only tasks belonging to *pet*.
            pet:         The Pet whose name is checked against *pet_name*.
                         Ignored when pet_name is None.
        """
        result = tasks
        if pending_only:
            result = [t for t in result if not t.is_completed]
        if pet_name is not None and pet is not None:
            if pet.name.lower() != pet_name.lower():
                result = []
        return result

    def detect_time_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return messages for any tasks whose preferred_time windows overlap."""
        timed = [
            (t,
             datetime.strptime(t.preferred_time, "%H:%M"),
             datetime.strptime(t.preferred_time, "%H:%M") + timedelta(minutes=t.duration_minutes))
            for t in tasks if t.preferred_time
        ]
        conflicts: list[str] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                t_a, start_a, end_a = timed[i]
                t_b, start_b, end_b = timed[j]
                if start_a < end_b and start_b < end_a:
                    conflicts.append(
                        f"'{t_a.name}' ({t_a.preferred_time}, {t_a.duration_minutes} min) "
                        f"overlaps with '{t_b.name}' ({t_b.preferred_time}, {t_b.duration_minutes} min)."
                    )
        return conflicts

    def fit_tasks(self, tasks: list[Task], time_limit: int) -> list[Task]:
        """Greedily select tasks that fit within time_limit minutes."""
        selected: list[Task] = []
        used = 0
        for task in tasks:
            if used + task.duration_minutes <= time_limit:
                selected.append(task)
                used += task.duration_minutes
        return selected

    def generate_plan(self, pet: Pet, available_time: int) -> DailyPlan:
        """Build a DailyPlan for *pet* within *available_time* minutes."""
        pending = pet.get_pending_tasks()
        prioritized = self.prioritize_tasks(pending)
        chosen = self.fit_tasks(prioritized, available_time)

        plan = DailyPlan(pet_id=pet.id, date=date.today())
        plan.conflicts = self.detect_time_conflicts(chosen)

        cursor = datetime.strptime(self.START_HOUR, "%H:%M")
        for task in chosen:
            # honour preferred_time if set, otherwise continue from cursor
            if task.preferred_time:
                start_dt = datetime.strptime(task.preferred_time, "%H:%M")
                # if preferred_time is already past the cursor, push cursor forward
                if start_dt < cursor:
                    plan.conflicts.append(
                        f"'{task.name}' preferred {task.preferred_time} "
                        f"but was rescheduled to {cursor.strftime('%H:%M')} due to earlier tasks."
                    )
                    start_dt = cursor
            else:
                start_dt = cursor

            end_dt = start_dt + timedelta(minutes=task.duration_minutes)
            plan.add_task(ScheduledTask(
                task=task,
                start_time=start_dt.strftime("%H:%M"),
                end_time=end_dt.strftime("%H:%M"),
            ))
            cursor = end_dt  # next task starts where this one ends

        plan.reasoning = self.explain_reasoning(plan, pet, available_time)
        return plan

    def explain_reasoning(
        self,
        plan: DailyPlan,
        pet: Optional[Pet] = None,
        available_time: Optional[int] = None,
    ) -> str:
        """Return a plain-English explanation of the scheduling decisions."""
        if not plan.scheduled_tasks:
            return "No tasks were scheduled (no pending tasks or no time available)."

        scheduled_names = [st.task.name for st in plan.scheduled_tasks]
        skipped: list[str] = []

        if pet is not None:
            scheduled_ids = {st.task.id for st in plan.scheduled_tasks}
            skipped = [
                t.name for t in pet.get_pending_tasks()
                if t.id not in scheduled_ids
            ]

        lines = [
            f"Scheduled {len(plan.scheduled_tasks)} task(s) "
            f"using {plan.total_time_minutes} of "
            f"{available_time or '?'} available minutes.",
            f"Included (by priority): {', '.join(scheduled_names)}.",
        ]
        if skipped:
            lines.append(f"Skipped (not enough time): {', '.join(skipped)}.")
        lines.append(
            "Tasks were ordered by priority (high → low) then duration "
            "(short → long) to maximise the number of tasks completed."
        )
        return " ".join(lines)
