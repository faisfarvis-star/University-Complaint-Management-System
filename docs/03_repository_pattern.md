# Repository Pattern

The one selected design pattern is **Repository**. UML: `diagrams/repository_uml.mmd`.

## Structure
- `app/repositories/interfaces/` – abstract base classes (`ComplaintRepository`, `UserRepository`,
  `CategoryRepository`, `NotificationRepository`, `ComplaintHistoryRepository`, plus
  `CommentRepository`, `AttachmentRepository`, `AuditLogRepository`).
- `app/repositories/implementations/` – concrete `SqlAlchemy…Repository` classes; the only place
  that runs queries.
- `app/services/factory.py` – composition root that injects the SQLAlchemy implementations.

## Rules enforced in the code
- Controllers never run queries; they call services.
- Services receive repositories through their constructor and only know the interfaces.
- Swapping storage means writing a new implementation – services and controllers do not change.

## Proof that it is a real pattern
`tests/test_repositories.py::test_mock_repository_can_replace_real_repository` builds a
`ComplaintService` with an `InMemoryComplaintRepository` (a plain-Python implementation of the
interface) and mock objects for the other repositories. Submitting and assigning a complaint works
with **no Flask app and no database**. A second test confirms the abstract interface cannot be
instantiated and that every SQLAlchemy class implements its interface.
