from pawpal_system import Owner, Pet, Task, TaskType, Scheduler


def print_section(title: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Create owner
    # ------------------------------------------------------------------
    owner = Owner(name="Maya", email="maya@example.com", time_available_minutes=90)

    # ------------------------------------------------------------------
    # 2. Create two pets
    # ------------------------------------------------------------------
    dog = Pet(name="Biscuit", species="Dog", breed="Beagle", age=3, weight=10.5)
    cat = Pet(name="Mochi",   species="Cat", breed="Tabby",  age=5, weight=4.2)

    owner.add_pet(dog)
    owner.add_pet(cat)

    # ------------------------------------------------------------------
    # 3. Add tasks to Biscuit (dog)
    # ------------------------------------------------------------------
    dog.add_task(Task(
        name="Morning Walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=5,
        preferred_time="07:00",
    ))
    dog.add_task(Task(
        name="Breakfast",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=5,
        preferred_time="08:00",
    ))
    dog.add_task(Task(
        name="Heartworm Pill",
        task_type=TaskType.MEDICATION,
        duration_minutes=5,
        priority=4,
        preferred_time="08:15",
    ))
    dog.add_task(Task(
        name="Fetch / Playtime",
        task_type=TaskType.ENRICHMENT,
        duration_minutes=20,
        priority=3,
        preferred_time="17:00",
    ))

    # ------------------------------------------------------------------
    # 4. Add tasks to Mochi (cat)
    # ------------------------------------------------------------------
    cat.add_task(Task(
        name="Breakfast",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=5,
        preferred_time="08:00",
    ))
    cat.add_task(Task(
        name="Brush Coat",
        task_type=TaskType.GROOMING,
        duration_minutes=15,
        priority=2,
        preferred_time="10:00",
    ))
    cat.add_task(Task(
        name="Interactive Toy Session",
        task_type=TaskType.ENRICHMENT,
        duration_minutes=15,
        priority=3,
        preferred_time="16:00",
    ))

    # ------------------------------------------------------------------
    # 5. Print owner + pets overview
    # ------------------------------------------------------------------
    print_section("Owner & Pets")
    print(f"  {owner}")
    for pet in owner.get_pets():
        print(f"  └─ {pet}")

    # ------------------------------------------------------------------
    # 6. Generate and print a schedule for each pet
    # ------------------------------------------------------------------
    scheduler = Scheduler()

    print_section("Today's Schedule")

    for pet in owner.get_pets():
        plan = scheduler.generate_plan(pet, owner.time_available_minutes)
        print(f"\n  🐾 {pet.name}")
        if not plan.scheduled_tasks:
            print("     No tasks scheduled.")
            continue
        for st in plan.scheduled_tasks:
            p = st.task.priority
            priority_bar = "█" * p + "░" * (5 - p)
            print(
                f"     {st.start_time} – {st.end_time}"
                f"  [{priority_bar}] "
                f"{st.task.name}  ({st.task.task_type.value}, {st.task.duration_minutes} min)"
            )
        print(f"\n     Total: {plan.total_time_minutes} min")
        print(f"     {plan.reasoning}")

    # ------------------------------------------------------------------
    # 7. All pending tasks across both pets (owner-level view)
    # ------------------------------------------------------------------
    print_section("All Pending Tasks (owner view)")
    for pet, task in owner.get_all_pending_tasks():
        print(f"  {pet.name:8s}  {task}")


if __name__ == "__main__":
    main()
