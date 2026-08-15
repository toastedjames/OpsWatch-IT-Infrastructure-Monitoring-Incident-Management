from datetime import datetime
import requests
from database import SessionLocal
from models import Metric, Incident
import psutil

from datetime import datetime

from database import SessionLocal

from models import Metric, Incident, Service


CPU_THRESHOLD = 85

MEMORY_THRESHOLD = 90

DISK_THRESHOLD = 90


def collect_metrics():

    cpu = psutil.cpu_percent(
        interval=1
    )

    memory = psutil.virtual_memory().percent

    disk = psutil.disk_usage("/").percent


    db = SessionLocal()


    metric = Metric(

        cpu_percent=cpu,

        memory_percent=memory,

        disk_percent=disk,

        timestamp=datetime.utcnow()

    )


    db.add(metric)

    db.commit()


    check_thresholds(
        db,
        cpu,
        memory,
        disk
    )


    db.close()


    return {

        "cpu": cpu,

        "memory": memory,

        "disk": disk

    }


def check_thresholds(
    db,
    cpu,
    memory,
    disk
):
    """
    Evaluate infrastructure thresholds and create
    incidents only when an equivalent incident is
    not already open.
    """

    # -----------------------------------------------------
    # CPU
    # -----------------------------------------------------

    if cpu >= CPU_THRESHOLD:

        create_incident_if_needed(
            db=db,
            incident_type="High CPU Utilization",
            severity="HIGH",
            description=(
                f"CPU utilization reached "
                f"{cpu:.1f}%, exceeding the "
                f"{CPU_THRESHOLD}% threshold."
            )
        )


    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    if memory >= MEMORY_THRESHOLD:

        create_incident_if_needed(
            db=db,
            incident_type="Memory Exhaustion",
            severity="CRITICAL",
            description=(
                f"Memory utilization reached "
                f"{memory:.1f}%, exceeding the "
                f"{MEMORY_THRESHOLD}% threshold."
            )
        )


    # -----------------------------------------------------
    # DISK
    # -----------------------------------------------------

    if disk >= DISK_THRESHOLD:

        create_incident_if_needed(
            db=db,
            incident_type="Disk Capacity Critical",
            severity="CRITICAL",
            description=(
                f"Disk utilization reached "
                f"{disk:.1f}%, exceeding the "
                f"{DISK_THRESHOLD}% threshold."
            )
        )

def create_incident_if_needed(
    db,
    incident_type,
    severity,
    description
):
    """
    Create an incident only if there is not
    already an OPEN incident of the same type.
    """

    existing_incident = (
        db.query(Incident)
        .filter(
            Incident.incident_type == incident_type,
            Incident.status == "OPEN"
        )
        .first()
    )


    # -----------------------------------------------------
    # Incident already exists
    # -----------------------------------------------------

    if existing_incident:

        print(
            f"[OpsWatch] Existing incident found: "
            f"{incident_type}"
        )

        return existing_incident


    # -----------------------------------------------------
    # Create new incident
    # -----------------------------------------------------

    incident = Incident(

        incident_type=incident_type,

        severity=severity,

        description=description,

        status="OPEN",

        detected_at=datetime.utcnow()

    )


    db.add(incident)

    db.commit()

    db.refresh(incident)


    print(
        f"[OpsWatch] NEW INCIDENT: "
        f"{incident_type} "
        f"({severity})"
    )


    return incident

    if cpu >= CPU_THRESHOLD:

        create_incident(

            db,

            "High CPU Utilization",

            "HIGH",

            f"CPU utilization reached {cpu:.1f}%"

        )


    if memory >= MEMORY_THRESHOLD:

        create_incident(

            db,

            "Memory Exhaustion",

            "CRITICAL",

            f"Memory utilization reached {memory:.1f}%"

        )


    if disk >= DISK_THRESHOLD:

        create_incident(

            db,

            "Disk Capacity Critical",

            "CRITICAL",

            f"Disk utilization reached {disk:.1f}%"

        )


def create_incident(
        db,
        incident_type,
        severity,
        description
):

    incident = Incident(

        incident_type=incident_type,

        severity=severity,

        description=description,

        status="OPEN",

        detected_at=datetime.utcnow()

    )


    db.add(incident)

    db.commit()

# =========================================================
# INCIDENT SIMULATION
# =========================================================

def simulate_incident(
    incident_type: str,
    severity: str,
    description: str
):

    db = SessionLocal()

    try:

        incident = Incident(
            incident_type=incident_type,
            severity=severity,
            description=description,
            status="OPEN",
            detected_at=datetime.utcnow()
        )

        db.add(incident)

        db.commit()

        db.refresh(incident)

        return incident

    finally:

        db.close()


def simulate_high_cpu():

    return simulate_incident(
        incident_type="High CPU Utilization",
        severity="HIGH",
        description=(
            "CPU utilization exceeded the "
            "85% operational threshold."
        )
    )


def simulate_memory_exhaustion():

    return simulate_incident(
        incident_type="Memory Exhaustion",
        severity="CRITICAL",
        description=(
            "Available system memory fell below "
            "the configured safety threshold."
        )
    )


def simulate_disk_capacity():

    return simulate_incident(
        incident_type="Disk Capacity Critical",
        severity="CRITICAL",
        description=(
            "Disk utilization exceeded 90%. "
            "Immediate capacity management is recommended."
        )
    )


def simulate_service_unavailable():

    return simulate_incident(
        incident_type="Service Unavailable",
        severity="HIGH",
        description=(
            "The monitored service failed to respond "
            "to consecutive availability checks."
        )
    )


def simulate_slow_response():

    return simulate_incident(
        incident_type="Slow Application Response",
        severity="MEDIUM",
        description=(
            "Application response time exceeded "
            "the configured performance threshold."
        )
    )


def simulate_ssl_expiry():

    return simulate_incident(
        incident_type="SSL Certificate Expiry",
        severity="MEDIUM",
        description=(
            "A monitored SSL certificate is approaching "
            "its expiration date."
        )
    )


def simulate_security_alert():

    return simulate_incident(
        incident_type="Security Alert",
        severity="CRITICAL",
        description=(
            "Multiple failed authentication attempts "
            "were detected from a monitored source."
        )
    )


def simulate_service_recovery():

    return simulate_incident(
        incident_type="Service Recovery",
        severity="LOW",
        description=(
            "A previously unavailable monitored service "
            "has successfully recovered."
        )
    )

# =========================================================
# SERVICE MONITORING
# =========================================================

def check_service(service_id):

    db = SessionLocal()

    try:

        service = (
            db.query(Service)
            .filter(
                Service.id == service_id
            )
            .first()
        )

        if not service:
            return {
                "error": "Service not found"
            }

        start_time = datetime.utcnow()

        try:

            response = requests.get(
                service.url,
                timeout=5
            )

            end_time = datetime.utcnow()

            response_time = (
                end_time - start_time
            ).total_seconds() * 1000

            service.response_time = response_time

            service.last_checked = end_time

            if response.status_code < 400:

                service.status = "UP"

            else:

                service.status = "DEGRADED"

        except requests.RequestException:

            end_time = datetime.utcnow()

            service.status = "DOWN"

            service.response_time = 0

            service.last_checked = end_time

        db.commit()

        return {
            "id": service.id,
            "name": service.name,
            "status": service.status,
            "response_time": service.response_time,
            "last_checked": service.last_checked
        }

    finally:

        db.close()

# =========================================================
# CREATE DEFAULT SERVICES
# =========================================================

def create_default_services():

    db = SessionLocal()

    try:

        if db.query(Service).count() > 0:
            return

        services = [

            Service(
                name="Graduate School Portal",
                url="https://www.vt.edu"
            ),

            Service(
                name="University Information Service",
                url="https://www.vt.edu"
            ),

            Service(
                name="FastAPI Monitoring Service",
                url="http://127.0.0.1:8000"
            )

        ]

        db.add_all(services)

        db.commit()

    finally:

        db.close()