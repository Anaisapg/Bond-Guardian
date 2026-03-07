from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class RitualStreak(Document):
    """Ritual streak tracking document model."""
    user_id: Indexed(str, unique=True)

    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_ritual_date: Optional[date] = None
    total_rituals: int = Field(default=0)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "ritual_streaks"
        use_state_management = True

    def complete_ritual(self):
        """Mark today's ritual as complete and update streak."""
        today = date.today()

        if self.last_ritual_date == today:
            # Already completed today
            return False

        if self.last_ritual_date:
            days_diff = (today - self.last_ritual_date).days

            if days_diff == 1:
                # Consecutive day - increase streak
                self.current_streak += 1
            elif days_diff > 1:
                # Streak broken - reset
                self.current_streak = 1
        else:
            # First ritual ever
            self.current_streak = 1

        # Update longest streak if needed
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        self.last_ritual_date = today
        self.total_rituals += 1
        self.updated_at = datetime.utcnow()

        return True


class RitualStreakResponse(BaseModel):
    """Schema for ritual streak response."""
    user_id: str
    current_streak: int
    longest_streak: int
    last_ritual_date: Optional[date]
    total_rituals: int
    completed_today: bool = False

    @classmethod
    def from_streak(cls, streak: RitualStreak) -> "RitualStreakResponse":
        """Create response from RitualStreak document."""
        completed_today = streak.last_ritual_date == date.today()

        return cls(
            user_id=streak.user_id,
            current_streak=streak.current_streak,
            longest_streak=streak.longest_streak,
            last_ritual_date=streak.last_ritual_date,
            total_rituals=streak.total_rituals,
            completed_today=completed_today,
        )
