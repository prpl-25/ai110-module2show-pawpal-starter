import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


from pawpal_system import Pet, Task, TaskType, Scheduler, Owner


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Test 3 — Sorting Correctness
# Tasks added in random order should come back sorted HH:MM ascending.
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    scheduler = Scheduler()

    evening   = Task("Evening Walk",   TaskType.WALK,      duration_minutes=30, priority=3, preferred_time="17:00")
    morning   = Task("Morning Feed",   TaskType.FEEDING,   duration_minutes=10, priority=5, preferred_time="07:00")
    midday    = Task("Midday Meds",    TaskType.MEDICATION, duration_minutes=5, priority=4, preferred_time="12:00")
    no_time   = Task("Free Play",      TaskType.ENRICHMENT, duration_minutes=20, priority=2)  # no preferred_time

    # deliberately shuffled
    tasks = [evening, no_time, morning, midday]

    sorted_tasks = scheduler.sort_by_time(tasks)
    times = [t.preferred_time if t.preferred_time else "99:99" for t in sorted_tasks]

    assert times == sorted(times), (
        f"Expected chronological order but got: {times}"
    )
    # tasks with no preferred_time must come last
    assert sorted_tasks[-1] == no_time


# ---------------------------------------------------------------------------
# Test 4 — Conflict Detection
# Two tasks whose time windows overlap should be flagged by the Scheduler.
# ---------------------------------------------------------------------------

def test_conflict_detection_flags_overlapping_tasks():
    scheduler = Scheduler()

    # walk starts at 08:00 and runs 30 min → ends 08:30
    walk = Task("Morning Walk", TaskType.WALK,    duration_minutes=30, priority=5, preferred_time="08:00")
    # feeding starts at 08:15, inside the walk window → overlap
    feed = Task("Breakfast",    TaskType.FEEDING, duration_minutes=10, priority=5, preferred_time="08:15")
    # grooming starts at 09:00, well after both → no conflict
    groom = Task("Grooming",    TaskType.GROOMING, duration_minutes=15, priority=2, preferred_time="09:00")

    conflicts = scheduler.detect_time_conflicts([walk, feed, groom])

    assert len(conflicts) == 1, (
        f"Expected exactly 1 conflict (walk ↔ feed) but got {len(conflicts)}: {conflicts}"
    )
    assert "Morning Walk" in conflicts[0]
    assert "Breakfast" in conflicts[0]


# ---------------------------------------------------------------------------
# Test 5 — Recurrence Logic  ← EXPECTED TO FAIL (feature not yet built)
#
# Desired behaviour: after a daily Task is marked complete, calling
# task.recur() should return a new Task scheduled for the following day,
# and adding it to the pet should increase the pet's task count by 1.
#
# FAILING SCENARIO INTERPRETATION
# --------------------------------
# Running this test produces:
#   AttributeError: 'Task' object has no attribute 'recur'
#
# This tells us recurrence is a missing feature, not a bug in existing code.
# The fix is to add a recur() method to Task that:
#   • creates a copy of the task with is_completed=False
#   • sets preferred_time to the same time (daily repeat)
#   • could store a next_due: date field to track when it runs next
# Until that method exists this test documents the gap and will remind us
# (via CI failure) that the feature is incomplete.
# ---------------------------------------------------------------------------

def test_recurrence_creates_next_day_task():
    pet = Pet(name="Mochi", species="Cat")
    daily_feed = Task(
        name="Breakfast",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=5,
        preferred_time="08:00",
    )
    pet.add_task(daily_feed)
    assert len(pet.get_tasks()) == 1

    # mark today's task done
    daily_feed.mark_complete()
    assert daily_feed.is_completed is True

    # recur() should hand back a fresh Task for tomorrow
    next_task = daily_feed.recur()                  # AttributeError — not implemented

    assert next_task.is_completed is False
    assert next_task.name == daily_feed.name
    assert next_task.preferred_time == daily_feed.preferred_time

    pet.add_task(next_task)
    assert len(pet.get_tasks()) == 2                # original + recurred task
