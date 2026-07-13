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


def _mapa_etl_job() -> None:
    db = SessionLocal()
    try:
        from app.mapa.etl import run_mapa_etl

        result = run_mapa_etl(db)
        print(
            f"[scheduler] ETL MAPA completado: {result.get('usos_indexed')} usos "
            f"({result.get('products_total')} productos fuente) en {result.get('elapsed_s')}s"
        )
    except Exception as exc:
        print(f"[scheduler] error ETL MAPA: {exc}")
    finally:
        db.close()


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return

    from app.climate.config import ETL_INTERVAL_SECONDS
    from app.mapa.config import ETL_CRON_DAY, ETL_CRON_HOUR

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(_alert_scan_job, "interval", minutes=30, id="alert_scan", replace_existing=True)
    scheduler.add_job(
        _climate_etl_job,
        "interval",
        seconds=ETL_INTERVAL_SECONDS,
        id="climate_etl",
        replace_existing=True,
    )
    scheduler.add_job(
        _mapa_etl_job,
        "cron",
        day_of_week=ETL_CRON_DAY,
        hour=ETL_CRON_HOUR,
        minute=0,
        id="mapa_etl",
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
