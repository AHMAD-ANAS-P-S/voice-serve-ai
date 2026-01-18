from enum import Enum

class DomainType(str, Enum):
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    GOVERNANCE = "governance"

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"

class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReminderType(str, Enum):
    EXAM = "exam"
    MEDICINE = "medicine"
    APPOINTMENT = "appointment"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class DocumentType(str, Enum):
    AADHAAR = "aadhaar"
    PAN = "pan"
    BANK = "bank"
