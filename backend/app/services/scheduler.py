"""Job programado: alertas fitosanitarias + ETL climático."""

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


def _climate_etl_job() -> None:
    db = SessionLocal()
    try:
        from app.climate.etl import run_climate_etl

        elapsed = run_climate_etl(db)
        print(f"[scheduler] ETL climate completado en {elapsed:.1f}s")
    except Exception as exc:
        print(f"[scheduler] error ETL climate: {exc}")
    finally:
        db.close()


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return

    from app.climate.config import ETL_INTERVAL_SECONDS

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(_alert_scan_job, "interval", minutes=30, id="alert_scan", replace_existing=True)
    scheduler.add_job(
        _climate_etl_job,
        "interval",
        seconds=ETL_INTERVAL_SECONDS,
        id="climate_etl",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    _alert_scan_job()
    _climate_etl_job()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
