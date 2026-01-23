from fastapi import APIRouter, HTTPException
import requests
from icalendar import Calendar
from datetime import datetime, date, timedelta
import pytz
from sqlmodel import select
from config import get_settings
from logger import setup_logger
from db import get_session
from models import Grade, GradeCreate, GradeImportPayload, GradeOut

settings = get_settings()
logger = setup_logger("hyperplanning")

router = APIRouter(prefix="/hyperplanning", tags=["hyperplanning"])

def parse_event(component):
    """Parse a single iCal event into a dictionary."""
    summary = str(component.get('summary'))
    location = str(component.get('location', ''))
    description = str(component.get('description', ''))
    dtstart = component.get('dtstart').dt
    dtend = component.get('dtend').dt

    # Handle timezone if present, otherwise assume local/Paris
    paris_tz = pytz.timezone("Europe/Paris")
    
    if not isinstance(dtstart, datetime):
        # It's a date object (all day event)
        start_str = "Toute la journée"
        end_str = ""
        # Convert to datetime for consistency in raw_start (midnight)
        dtstart = datetime.combine(dtstart, datetime.min.time()).replace(tzinfo=paris_tz)
        dtend = datetime.combine(dtend, datetime.min.time()).replace(tzinfo=paris_tz)
    else:
        # Ensure timezone awareness and convert to Paris
        if dtstart.tzinfo is None:
            dtstart = pytz.UTC.localize(dtstart)
        if dtend.tzinfo is None:
            dtend = pytz.UTC.localize(dtend)
            
        dtstart = dtstart.astimezone(paris_tz)
        dtend = dtend.astimezone(paris_tz)

        # Convert to string format HH:MM
        start_str = dtstart.strftime("%H:%M")
        end_str = dtend.strftime("%H:%M")

    # Extract teacher/type from description if possible (heuristics)
    # Description often contains: "Matière : ... \n Enseignant : ... \n Type : ..."
    teacher = "Inconnu"
    type_cours = "Cours"
    
    if "Enseignant :" in description:
        parts = description.split("Enseignant :")
        if len(parts) > 1:
            teacher = parts[1].split("\n")[0].strip()
            
    if "Type :" in description:
        parts = description.split("Type :")
        if len(parts) > 1:
            type_cours = parts[1].split("\n")[0].strip()

    logger.debug(f"Parsed event: {summary} on {dtstart.date()}")

    return {
        "id": str(component.get('uid')),
        "subject": summary,
        "start": start_str,
        "end": end_str,
        "room": location,
        "teacher": teacher,
        "type": type_cours,
        "raw_start": dtstart.isoformat(),
        "raw_end": dtend.isoformat()
    }

@router.get("/courses")
def get_courses():
    """Fetch courses for the next active day (today or next working day)."""
    try:
        response = requests.get(settings.hyperplanning_url)
        response.raise_for_status()
        
        cal = Calendar.from_ical(response.content)
        
        # Find the next day with courses, starting today
        paris_tz = pytz.timezone("Europe/Paris")
        now = datetime.now(paris_tz).date()
        target_date = now
        found_courses = []
        
        # Look ahead up to 7 days
        for i in range(8):
            check_date = now + timedelta(days=i)
            daily_courses = []
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    parsed = parse_event(component)
                    if not parsed:
                        continue
                        
                    # Parse raw_start back to datetime to check date
                    # raw_start is isoformat string from parse_event (Paris time)
                    start_dt = datetime.fromisoformat(parsed['raw_start'])
                    
                    if start_dt.date() == check_date:
                        daily_courses.append(parsed)
            
            if daily_courses:
                found_courses = daily_courses
                target_date = check_date
                logger.info(f"Found {len(daily_courses)} courses for {target_date}")
                break
        
        # Sort by start time
        found_courses.sort(key=lambda x: x['start'])
        
        # Format date for display (e.g., "Lundi 24 Nov")
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        months = ["Jan", "Fév", "Mars", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
        
        display_date = "Aujourd'hui"
        if target_date != now:
            day_name = days[target_date.weekday()]
            month_name = months[target_date.month - 1]
            display_date = f"{day_name} {target_date.day} {month_name}"

        return {
            "date": target_date.isoformat(),
            "display_date": display_date,
            "courses": found_courses
        }

    except Exception as e:
        logger.error(f"Error fetching Hyperplanning courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch courses from Hyperplanning")

@router.get("/next-courses")
def get_next_courses():
    """Fetch the next 5 upcoming courses starting from now."""
    try:
        response = requests.get(settings.hyperplanning_url)
        response.raise_for_status()
        
        cal = Calendar.from_ical(response.content)
        
        now = datetime.now(pytz.UTC)
        upcoming_courses = []
        
        for component in cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get('dtstart').dt
                
                # Handle timezone
                if isinstance(dtstart, datetime):
                    if dtstart.tzinfo is None:
                        dtstart = pytz.UTC.localize(dtstart)
                else:
                    # All-day event (date object)
                    dtstart = datetime.combine(dtstart, datetime.min.time()).replace(tzinfo=pytz.UTC)
                
                if dtstart > now:
                    parsed = parse_event(component)
                    if parsed:
                        # Add raw start for sorting
                        parsed['_dt'] = dtstart
                        upcoming_courses.append(parsed)
        
        # Sort by time and take top 5
        upcoming_courses.sort(key=lambda x: x['_dt'])
        next_5 = upcoming_courses[:5]
        
        # Clean up internal key
        for c in next_5:
            del c['_dt']
            
        return next_5

    except Exception as e:
        logger.error(f"Error fetching next courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch next courses")

@router.get("/stats")
def get_stats():
    """Calculate hours per subject from iCal."""
    try:
        response = requests.get(settings.hyperplanning_url)
        response.raise_for_status()
        
        cal = Calendar.from_ical(response.content)
        
        subjects = {}
        now = datetime.now(pytz.UTC)
        
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary'))
                dtstart = component.get('dtstart').dt
                dtend = component.get('dtend').dt
                
                # Handle timezone
                if isinstance(dtstart, datetime):
                    if dtstart.tzinfo is None:
                        dtstart = pytz.UTC.localize(dtstart)
                    if dtend.tzinfo is None:
                        dtend = pytz.UTC.localize(dtend)
                else:
                    # Date object (all day), skip for stats or assume 7h?
                    # Usually courses have times. Skip all-day for now.
                    continue

                duration = (dtend - dtstart).total_seconds() / 3600
                
                if summary not in subjects:
                    subjects[summary] = {"done": 0, "planned": 0, "total": 0}
                
                subjects[summary]["total"] += duration
                
                if dtend < now:
                    subjects[summary]["done"] += duration
                else:
                    subjects[summary]["planned"] += duration
        
        # Format for frontend
        stats = []
        for name, data in subjects.items():
            stats.append({
                "subject": name,
                "done": round(data["done"], 1),
                "planned": round(data["planned"], 1),
                "total": round(data["total"], 1)
            })
            
        # Sort by total hours desc
        stats.sort(key=lambda x: x['total'], reverse=True)
        
        return stats

    except Exception as e:
        logger.error(f"Error fetching Hyperplanning stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Hyperplanning statistics")


# === GRADES ENDPOINTS ===

@router.get("/grades", response_model=list[GradeOut])
def get_grades():
    """Fetch all grades, sorted by creation date (most recent first)."""
    try:
        with get_session() as session:
            statement = select(Grade).order_by(Grade.created_at.desc())
            grades = list(session.exec(statement))
            return grades
    except Exception as e:
        logger.error(f"Error fetching grades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grades/import")
def import_grades(payload: GradeImportPayload):
    """Bulk import grades (replaces all existing grades)."""
    try:
        with get_session() as session:
            # Delete all old grades
            statement = select(Grade)
            old_grades = list(session.exec(statement))
            for grade in old_grades:
                session.delete(grade)

            # Add new grades
            new_grades = []
            for grade_data in payload.grades:
                grade = Grade(
                    subject=grade_data.subject,
                    date=grade_data.date,
                    value=grade_data.value
                )
                session.add(grade)
                new_grades.append(grade)

            session.commit()

            # Refresh to get IDs
            for grade in new_grades:
                session.refresh(grade)

            return {
                "message": f"{len(new_grades)} grade(s) imported successfully",
                "count": len(new_grades)
            }

    except Exception as e:
        logger.error(f"Error importing grades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/grades/clear")
def clear_grades():
    """Delete all grades."""
    try:
        with get_session() as session:
            statement = select(Grade)
            grades = list(session.exec(statement))
            count = len(grades)

            for grade in grades:
                session.delete(grade)

            session.commit()

            return {
                "message": f"{count} grade(s) deleted",
                "count": count
            }

    except Exception as e:
        logger.error(f"Error clearing grades: {e}")
        raise HTTPException(status_code=500, detail=str(e))
