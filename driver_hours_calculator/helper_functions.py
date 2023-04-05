from datetime import datetime, timedelta

def get_previous_sunday(offset_weeks: int=0) -> datetime:
    """Returns a sunday based on offset weeks.
        e.g. Today is Monday 3/20 offset_week being 0 will return Sunday 3/19. offset_week == 1 will return Sunday 3/12
    """
    days_in_week = 7
    today = datetime.today()
    index = (today.weekday() + 1) % days_in_week
    sunday = today - timedelta(days_in_week + index)
    sunday = sunday - timedelta(weeks=offset_weeks-1)#This feels wonky but works
    sunday = sunday.replace(hour=0, minute=0, second=0, microsecond=0)
    return sunday