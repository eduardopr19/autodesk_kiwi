from datetime import datetime, timedelta

import pytz
import requests
from fastapi import APIRouter, HTTPException
from icalendar import Calendar
from sqlmodel import select

from config import get_settings
from db import get_session
from logger import setup_logger
from models import Grade, GradeImportPayload, GradeOut

settings = get_settings()
logger = setup_logger("hyperplanning")

router = APIRouter(prefix="/hyperplanning", tags=["hyperplanning"])

def parse_event(component):
    summary = str(component.get('summary'))
    location = str(component.get('location', ''))
    description = str(component.get('description', ''))
    dtstart = component.get('dtstart').dt
    dtend = component.get('dtend').dt

    paris_tz = pytz.timezone("Europe/Paris")

    if not isinstance(dtstart, datetime):
        start_str = "Toute la journée"
        end_str = ""
        dtstart = datetime.combine(dtstart, datetime.min.time()).replace(tzinfo=paris_tz)
        dtend = datetime.combine(dtend, datetime.min.time()).replace(tzinfo=paris_tz)
    else:
        if dtstart.tzinfo is None:
            dtstart = pytz.UTC.localize(dtstart)
        if dtend.tzinfo is None:
            dtend = pytz.UTC.localize(dtend)

        dtstart = dtstart.astimezone(paris_tz)
        dtend = dtend.astimezone(paris_tz)

        start_str = dtstart.strftime("%H:%M")
        end_str = dtend.strftime("%H:%M")

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
    try:
        response = requests.get(settings.hyperplanning_url)
        response.raise_for_status()

        cal = Calendar.from_ical(response.content)

        paris_tz = pytz.timezone("Europe/Paris")
        now = datetime.now(paris_tz).date()
        target_date = now
        found_courses = []

        for i in range(8):
            check_date = now + timedelta(days=i)
            daily_courses = []

            for component in cal.walk():
                if component.name == "VEVENT":
                    parsed = parse_event(component)
                    if not parsed:
                        continue

                    start_dt = datetime.fromisoformat(parsed['raw_start'])

                    if start_dt.date() == check_date:
                        daily_courses.append(parsed)

            if daily_courses:
                found_courses = daily_courses
                target_date = check_date
                logger.info(f"Found {len(daily_courses)} courses for {target_date}")
                break

        found_courses.sort(key=lambda x: x['start'])

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
        raise HTTPException(status_code=500, detail="Failed to fetch courses from Hyperplanning") from None

@router.get("/next-courses")
def get_next_courses():
    try:
        response = requests.get(settings.hyperplanning_url)
        response.raise_for_status()

        cal = Calendar.from_ical(response.content)

        now = datetime.now(pytz.UTC)
        upcoming_courses = []

        for component in cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get('dtstart').dt

                if isinstance(dtstart, datetime):
                    if dtstart.tzinfo is None:
                        dtstart = pytz.UTC.localize(dtstart)
                else:
                    dtstart = datetime.combine(dtstart, datetime.min.time()).replace(tzinfo=pytz.UTC)

                if dtstart > now:
                    parsed = parse_event(component)
                    if parsed:
                        parsed['_dt'] = dtstart
                        upcoming_courses.append(parsed)

        upcoming_courses.sort(key=lambda x: x['_dt'])
        next_5 = upcoming_courses[:5]

        for c in next_5:
            del c['_dt']

        return next_5

    except Exception as e:
        logger.error(f"Error fetching next courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch next courses") from None

@router.get("/stats")
def get_stats():
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

                if isinstance(dtstart, datetime):
                    if dtstart.tzinfo is None:
                        dtstart = pytz.UTC.localize(dtstart)
                    if dtend.tzinfo is None:
                        dtend = pytz.UTC.localize(dtend)
                else:
                    continue

                duration = (dtend - dtstart).total_seconds() / 3600

                if summary not in subjects:
                    subjects[summary] = {"done": 0, "planned": 0, "total": 0}

                subjects[summary]["total"] += duration

                if dtend < now:
                    subjects[summary]["done"] += duration
                else:
                    subjects[summary]["planned"] += duration

        stats = []
        for name, data in subjects.items():
            stats.append({
                "subject": name,
                "done": round(data["done"], 1),
                "planned": round(data["planned"], 1),
                "total": round(data["total"], 1)
            })

        stats.sort(key=lambda x: x['total'], reverse=True)

        return stats

    except Exception as e:
        logger.error(f"Error fetching Hyperplanning stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Hyperplanning statistics") from None


@router.get("/grades", response_model=list[GradeOut])
def get_grades():
    try:
        with get_session() as session:
            statement = select(Grade).order_by(Grade.created_at.desc())
            grades = list(session.exec(statement))
            return grades
    except Exception as e:
        logger.error(f"Error fetching grades: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.post("/grades/import")
def import_grades(payload: GradeImportPayload):
    try:
        with get_session() as session:
            statement = select(Grade)
            old_grades = list(session.exec(statement))
            for grade in old_grades:
                session.delete(grade)

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

            for grade in new_grades:
                session.refresh(grade)

            return {
                "message": f"{len(new_grades)} grade(s) imported successfully",
                "count": len(new_grades)
            }

    except Exception as e:
        logger.error(f"Error importing grades: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.delete("/grades/clear")
def clear_grades():
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
        raise HTTPException(status_code=500, detail=str(e)) from None
