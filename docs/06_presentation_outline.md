# 10-minute presentation outline

| Time | Slide | Speaker notes |
|------|-------|---------------|
| 1 min | 1. Title + problem | "Complaints get lost in email and paper. Students can't see progress; management can't see patterns." |
| 2 min | 2. Objectives and features | Three roles. Walk through the workflow diagram: Pending → Assigned → In Progress → Resolved → Closed, with reopen. |
| 2 min | 3. MVC | Open the folder tree: `models/`, `templates/`, `controllers/`. Show `controllers/student.py` – short, no SQL. Say: the services layer holds business rules *inside* MVC. |
| 2 min | 4. Repository Pattern | Show `interfaces/complaint_repository.py`, then `implementations/complaint_repository.py`. Show the mock-repository test and say "service runs without a database". |
| 2 min | 5. Live demo | (1) student1 submits complaint with a PDF. (2) admin sees dashboard, assigns to staff. (3) staff starts and resolves with a note. (4) admin closes. (5) student sees history + notification. Finish with the 403 when staff opens another complaint. |
| 1 min | 6. Conclusion | Real persistence, enforced workflow, security basics, 48 passing tests. Future: email alerts, SLA timers. |

Demo tip: run `flask --app run seed --reset` before the demo and keep three browser profiles (admin / staff / student) logged in.
