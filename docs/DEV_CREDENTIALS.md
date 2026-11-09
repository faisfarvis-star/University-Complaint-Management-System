# Development login credentials (fictional, development only)

Created by `flask --app run seed`. **Never use these in a real deployment.**

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@ucms-demo.edu | Admin@12345 |
| Staff (x3) | staff1@ucms-demo.edu … staff3@ucms-demo.edu | Staff@12345 |
| Student (x5) | student1@ucms-demo.edu … student5@ucms-demo.edu | Student@12345 |

Real admin accounts are created with `flask --app run create-admin`; staff accounts are created
by an admin under **Staff → Add staff member**. Public registration only ever creates students.
