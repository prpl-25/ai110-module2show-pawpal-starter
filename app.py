import streamlit as st
from pawpal_system import Owner, Pet, Task, TaskType, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session-state bootstrap — create objects once, survive reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None   # set after owner form is submitted

if "pets" not in st.session_state:
    st.session_state.pets = {}      # pet_name -> Pet instance

# ---------------------------------------------------------------------------
# Section 1: Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner Info")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value="Jordan")
with col2:
    time_available = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=480, value=90
    )

if st.button("Save owner"):
    st.session_state.owner = Owner(
        name=owner_name,
        time_available_minutes=int(time_available),
    )
    st.success(f"Owner saved: {st.session_state.owner}")

owner: Owner | None = st.session_state.owner

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Add a pet  →  calls Owner.add_pet()
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    breed = st.text_input("Breed (optional)", value="")

if st.button("Add pet"):
    if owner is None:
        st.warning("Save your owner info first.")
    elif pet_name in st.session_state.pets:
        st.warning(f"{pet_name} is already added.")
    else:
        new_pet = Pet(name=pet_name, species=species, breed=breed)
        owner.add_pet(new_pet)                          # <- Phase 2 method
        st.session_state.pets[pet_name] = new_pet
        st.success(f"Added pet: {new_pet}")

if st.session_state.pets:
    st.write("**Your pets:**", ", ".join(st.session_state.pets.keys()))

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Add a task to a pet  →  calls Pet.add_task()
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

PRIORITY_MAP = {"Low (1)": 1, "Medium (3)": 3, "High (5)": 5}
TYPE_MAP = {t.value: t for t in TaskType}

col1, col2 = st.columns(2)
with col1:
    task_pet = st.selectbox(
        "Assign to pet",
        options=list(st.session_state.pets.keys()) or ["—"],
    )
with col2:
    task_type = st.selectbox("Task type", options=list(TYPE_MAP.keys()))

col3, col4, col5 = st.columns(3)
with col3:
    task_title = st.text_input("Task name", value="Morning walk")
with col4:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col5:
    priority_label = st.selectbox("Priority", options=list(PRIORITY_MAP.keys()), index=2)

preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")

if st.button("Add task"):
    if owner is None:
        st.warning("Save your owner info first.")
    elif task_pet not in st.session_state.pets:
        st.warning("Add a pet before adding tasks.")
    else:
        pet: Pet = st.session_state.pets[task_pet]
        new_task = Task(
            name=task_title,
            task_type=TYPE_MAP[task_type],
            duration_minutes=int(duration),
            priority=PRIORITY_MAP[priority_label],
            preferred_time=preferred_time.strip() or None,
        )
        pet.add_task(new_task)                          # <- Phase 2 method
        st.success(f"Task added to {pet.name}: {new_task}")

# Show current task list per pet — with filter controls
if st.session_state.pets:
    st.markdown("**Filter tasks**")
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        filter_pending = st.checkbox("Pending only", value=False)
    with fcol2:
        type_options = ["All"] + [t.value for t in TaskType]
        filter_type_label = st.selectbox("Type", type_options, key="filter_type")
        filter_type = TYPE_MAP.get(filter_type_label)  # None when "All"
    with fcol3:
        filter_min_priority = st.slider("Min priority", min_value=1, max_value=5, value=1)

    for pname, pet in st.session_state.pets.items():
        tasks = pet.get_tasks_filtered(
            task_type=filter_type,
            min_priority=filter_min_priority,
            pending_only=filter_pending,
        )
        if tasks:
            with st.expander(f"{pname}'s tasks ({len(tasks)})"):
                for t in tasks:
                    st.write(f"- {t}")

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate schedule  →  calls Scheduler.generate_plan()
# ---------------------------------------------------------------------------
st.subheader("Generate Today's Schedule")

if st.button("Generate schedule"):
    if owner is None:
        st.warning("Save your owner info first.")
    elif not st.session_state.pets:
        st.warning("Add at least one pet with tasks first.")
    else:
        scheduler = Scheduler()
        for pname, pet in st.session_state.pets.items():
            plan = scheduler.generate_plan(             # <- Phase 2 method
                pet, owner.time_available_minutes
            )
            st.markdown(f"### {pname}'s Plan")
            if not plan.scheduled_tasks:
                st.info("No pending tasks to schedule.")
                continue

            rows = [
                {
                    "Time": f"{sched.start_time} – {sched.end_time}",
                    "Task": sched.task.name,
                    "Type": sched.task.task_type.value,
                    "Duration (min)": sched.task.duration_minutes,
                    "Priority": sched.task.priority,
                }
                for sched in plan.scheduled_tasks
            ]
            st.table(rows)
            st.caption(f"Total: {plan.total_time_minutes} min")
            if plan.conflicts:
                with st.expander(f"⚠️ {len(plan.conflicts)} scheduling conflict(s)"):
                    for msg in plan.conflicts:
                        st.warning(msg)
            with st.expander("Reasoning"):
                st.write(plan.reasoning)
