"""NEXO Climate — tablas agregadas Open-Meteo (PostgreSQL)."""

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String

from app.db.base import Base


class ClimateDaily(Base):
    __tablename__ = "climate_daily"

    station_id = Column(Integer, ForeignKey("climate_stations.id"), primary_key=True)
    fecha = Column(Date, primary_key=True)
    et0_diaria = Column(Float, nullable=True)
    radiacion_diaria = Column(Float, nullable=True)
    temperatura_media = Column(Float, nullable=True)
    humedad_media = Column(Float, nullable=True)
    viento_medio = Column(Float, nullable=True)
    precipitacion_diaria = Column(Float, nullable=True)
    estres_termico_medio = Column(Float, nullable=True)


class ClimateWeekly(Base):
    __tablename__ = "climate_weekly"

    station_id = Column(Integer, ForeignKey("climate_stations.id"), primary_key=True)
    semana_id = Column(String(10), primary_key=True)
    et0_semanal = Column(Float, nullable=True)
    radiacion_semanal = Column(Float, nullable=True)
    temperatura_media_semanal = Column(Float, nullable=True)
    humedad_media_semanal = Column(Float, nullable=True)
    viento_medio_semanal = Column(Float, nullable=True)
    precipitacion_semanal = Column(Float, nullable=True)
    estres_termico_semanal = Column(Float, nullable=True)


class ClimateMonthly(Base):
    __tablename__ = "climate_monthly"

    station_id = Column(Integer, ForeignKey("climate_stations.id"), primary_key=True)
    mes = Column(String(7), primary_key=True)
    et0_mensual = Column(Float, nullable=True)
    radiacion_mensual = Column(Float, nullable=True)
    temperatura_media_mes = Column(Float, nullable=True)
    humedad_media_mes = Column(Float, nullable=True)
    viento_medio_mes = Column(Float, nullable=True)
    precipitacion_mensual = Column(Float, nullable=True)
    estres_termico_mes = Column(Float, nullable=True)
