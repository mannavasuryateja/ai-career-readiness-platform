from typing import Dict, Optional
import uuid
from app.models.schemas import SessionData


class SessionStore:
    """In-memory session storage"""

    def __init__(self):
        self._store: Dict[str, SessionData] = {}

    def create_session(self, interview_type: str, mode: str, **kwargs) -> SessionData:
        """Create a new session and store it"""
        session_id = str(uuid.uuid4())
        
        session = SessionData(
            session_id=session_id,
            interview_type=interview_type,
            mode=mode,
            **kwargs
        )
        
        self._store[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve a session by ID"""
        return self._store.get(session_id)

    def update_session(self, session_id: str, updates: Dict) -> Optional[SessionData]:
        """Update session fields"""
        session = self._store.get(session_id)
        if session:
            for key, value in updates.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            self._store[session_id] = session
            return session
        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return session_id in self._store


# Global session store instance
session_store = SessionStore()
