"""Job programado de escaneo de alertas (cada 30 min)."""

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.services.alert_engine import run_alert_scan

_scheduler: BackgroundScheduler | None = None


def _alert_scan_job() -> None:
    db = SessionLocal()
    try:
        created = run_alert_scan(db)
        print(f"[scheduler] escaneo de alertas: {created} nueva(s)")
    except Exception as exc:
        print(f"[scheduler] error en escaneo de alertas: {exc}")
    finally:
        db.close()


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(_alert_scan_job, "interval", minutes=30, id="alert_scan", replace_existing=True)
    scheduler.start()
    _scheduler = scheduler
    _alert_scan_job()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
