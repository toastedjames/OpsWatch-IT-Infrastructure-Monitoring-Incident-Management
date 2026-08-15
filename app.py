from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy import desc

from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from database import Base, engine, get_db

from models import Metric, Incident, Service

from monitoring import (
    collect_metrics,
    create_default_services,
    check_service,
    simulate_high_cpu,
    simulate_memory_exhaustion,
    simulate_disk_capacity,
    simulate_service_unavailable,
    simulate_slow_response,
    simulate_ssl_expiry,
    simulate_security_alert,
    simulate_service_recovery
)


# =========================================================
# BACKGROUND MONITORING
# =========================================================

scheduler = BackgroundScheduler()


def scheduled_monitoring():

    try:

        result = collect_metrics()

        print(
            f"[OpsWatch] Metrics collected: "
            f"CPU={result['cpu']:.1f}% "
            f"MEM={result['memory']:.1f}% "
            f"DISK={result['disk']:.1f}%"
        )

    except Exception as error:

        print(
            f"[OpsWatch] Monitoring error: {error}"
        )


@asynccontextmanager
async def lifespan(app):

    scheduler.add_job(
        scheduled_monitoring,
        "interval",
        seconds=30,
        id="system_monitoring",
        replace_existing=True
    )

    scheduler.start()

    print(
        "[OpsWatch] Background monitoring started."
    )

    yield

    scheduler.shutdown()

    print(
        "[OpsWatch] Background monitoring stopped."
    )


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="OpsWatch",
    description=(
        "IT Infrastructure Monitoring "
        "and Incident Management Platform"
    ),
    version="1.0.0",
    lifespan=lifespan
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# TEMPLATES
# =========================================================

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(
    bind=engine
)

create_default_services()


# =========================================================
# DASHBOARD
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    latest_metric = (
        db.query(Metric)
        .order_by(
            desc(Metric.timestamp)
        )
        .first()
    )

    incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "OPEN"
        )
        .order_by(
            desc(Incident.detected_at)
        )
        .limit(10)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "metric": latest_metric,
            "incidents": incidents
        }
    )


# =========================================================
# INCIDENTS PAGE
# =========================================================

@app.get(
    "/incidents",
    response_class=HTMLResponse
)
def incidents_page(
    request: Request,
    db: Session = Depends(get_db)
):

    incidents = (
        db.query(Incident)
        .order_by(
            desc(Incident.detected_at)
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="incidents.html",
        context={
            "incidents": incidents
        }
    )


# =========================================================
# SERVICES PAGE
# =========================================================

@app.get(
    "/services",
    response_class=HTMLResponse
)
def services_page(
    request: Request,
    db: Session = Depends(get_db)
):

    services = (
        db.query(Service)
        .order_by(
            Service.name
        )
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="services.html",
        context={
            "services": services
        }
    )


# =========================================================
# METRICS PAGE
# =========================================================

@app.get(
    "/metrics",
    response_class=HTMLResponse
)
def metrics_page(
    request: Request,
    db: Session = Depends(get_db)
):

    metrics = (
        db.query(Metric)
        .order_by(
            desc(Metric.timestamp)
        )
        .limit(100)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="metrics.html",
        context={
            "metrics": metrics
        }
    )


# =========================================================
# REPORTS PAGE
# =========================================================

@app.get(
    "/reports",
    response_class=HTMLResponse
)
def reports_page(
    request: Request,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Incident totals
    # -----------------------------------------------------

    total_incidents = (
        db.query(Incident)
        .count()
    )

    open_incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "OPEN"
        )
        .count()
    )

    resolved_incidents = (
        db.query(Incident)
        .filter(
            Incident.status == "RESOLVED"
        )
        .count()
    )


    # -----------------------------------------------------
    # Severity counts
    # -----------------------------------------------------

    critical_count = (
        db.query(Incident)
        .filter(
            Incident.severity == "CRITICAL"
        )
        .count()
    )

    high_count = (
        db.query(Incident)
        .filter(
            Incident.severity == "HIGH"
        )
        .count()
    )

    medium_count = (
        db.query(Incident)
        .filter(
            Incident.severity == "MEDIUM"
        )
        .count()
    )

    low_count = (
        db.query(Incident)
        .filter(
            Incident.severity == "LOW"
        )
        .count()
    )


    # -----------------------------------------------------
    # Services
    # -----------------------------------------------------

    services = (
        db.query(Service)
        .order_by(
            Service.name
        )
        .all()
    )


    # -----------------------------------------------------
    # Recent incidents
    # -----------------------------------------------------

    recent_incidents = (
        db.query(Incident)
        .order_by(
            desc(Incident.detected_at)
        )
        .limit(8)
        .all()
    )


    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={

            "total_incidents":
                total_incidents,

            "open_incidents":
                open_incidents,

            "resolved_incidents":
                resolved_incidents,

            "critical_count":
                critical_count,

            "high_count":
                high_count,

            "medium_count":
                medium_count,

            "low_count":
                low_count,

            "services":
                services,

            "recent_incidents":
                recent_incidents
        }
    )


# =========================================================
# API — CURRENT METRICS
# =========================================================

@app.get(
    "/api/metrics"
)
def metrics_api(
    db: Session = Depends(get_db)
):

    metric = (
        db.query(Metric)
        .order_by(
            desc(Metric.timestamp)
        )
        .first()
    )

    if not metric:

        return {
            "message":
                "No metrics collected yet."
        }

    return {

        "cpu":
            metric.cpu_percent,

        "memory":
            metric.memory_percent,

        "disk":
            metric.disk_percent,

        "timestamp":
            metric.timestamp
    }


# =========================================================
# API — COLLECT METRICS
# =========================================================

@app.post(
    "/api/collect"
)
def collect():

    return collect_metrics()


# =========================================================
# API — INCIDENTS
# =========================================================

@app.get(
    "/api/incidents"
)
def incidents_api(
    db: Session = Depends(get_db)
):

    incidents = (
        db.query(Incident)
        .order_by(
            desc(Incident.detected_at)
        )
        .all()
    )

    return [

        {
            "id":
                incident.id,

            "type":
                incident.incident_type,

            "severity":
                incident.severity,

            "description":
                incident.description,

            "status":
                incident.status,

            "detected_at":
                incident.detected_at
        }

        for incident in incidents

    ]


# =========================================================
# API — RESOLVE INCIDENT
# =========================================================

@app.post(
    "/api/incidents/{incident_id}/resolve"
)
def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):

    incident = (
        db.query(Incident)
        .filter(
            Incident.id == incident_id
        )
        .first()
    )

    if not incident:

        return {
            "error":
                "Incident not found"
        }

    from datetime import datetime

    incident.status = "RESOLVED"

    incident.resolved_at = datetime.utcnow()

    db.commit()

    db.refresh(incident)

    return {

        "message":
            "Incident resolved successfully",

        "id":
            incident.id,

        "status":
            incident.status,

        "resolved_at":
            incident.resolved_at
    }


# =========================================================
# API — INCIDENT SIMULATION
# =========================================================

@app.post(
    "/api/simulate/{incident_type}"
)
def simulate_incident_api(
    incident_type: str
):

    simulations = {

        "cpu":
            simulate_high_cpu,

        "memory":
            simulate_memory_exhaustion,

        "disk":
            simulate_disk_capacity,

        "service":
            simulate_service_unavailable,

        "performance":
            simulate_slow_response,

        "ssl":
            simulate_ssl_expiry,

        "security":
            simulate_security_alert,

        "recovery":
            simulate_service_recovery
    }

    if incident_type not in simulations:

        return {
            "error":
                "Unknown simulation type"
        }

    incident = simulations[
        incident_type
    ]()

    return {

        "message":
            "Incident simulated successfully",

        "id":
            incident.id,

        "type":
            incident.incident_type,

        "severity":
            incident.severity,

        "status":
            incident.status
    }


# =========================================================
# API — CHECK SERVICE
# =========================================================

@app.post(
    "/api/services/{service_id}/check"
)
def check_service_api(
    service_id: int
):

    return check_service(
        service_id
    )


# =========================================================
# API — LIST SERVICES
# =========================================================

@app.get(
    "/api/services"
)
def services_api(
    db: Session = Depends(get_db)
):

    services = (
        db.query(Service)
        .order_by(
            Service.name
        )
        .all()
    )

    return [

        {
            "id":
                service.id,

            "name":
                service.name,

            "url":
                service.url,

            "status":
                service.status,

            "response_time":
                service.response_time,

            "last_checked":
                service.last_checked
        }

        for service in services

    ]


# =========================================================
# API — SYSTEM HEALTH
# =========================================================

@app.get(
    "/api/health"
)
def system_health():

    return {

        "application":
            "OpsWatch",

        "status":
            "UP",

        "version":
            "1.0.0"
    }