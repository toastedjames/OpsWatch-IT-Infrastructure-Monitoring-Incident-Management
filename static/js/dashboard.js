// =========================================================
// OpsWatch JavaScript
// =========================================================


// ---------------------------------------------------------
// Collect Metrics
// ---------------------------------------------------------

async function collectMetrics() {

    const button =
        document.querySelector(".refresh-button");


    try {

        if (button) {

            button.disabled = true;

            button.textContent =
                "Collecting...";

        }


        const response =
            await fetch(
                "/api/collect",
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Metric collection failed."
            );

        }


        const data =
            await response.json();


        console.log(
            "Metrics collected:",
            data
        );


        window.location.reload();


    } catch (error) {

        console.error(error);

        alert(
            "Unable to collect system metrics."
        );


        if (button) {

            button.disabled = false;

            button.textContent =
                "Collect Metrics";

        }

    }

}


// ---------------------------------------------------------
// Incident filtering
// ---------------------------------------------------------

function filterIncidents() {

    const search =
        document
            .getElementById("incidentSearch")
            .value
            .toLowerCase();


    const severity =
        document
            .getElementById("severityFilter")
            .value;


    const status =
        document
            .getElementById("statusFilter")
            .value;


    const rows =
        document.querySelectorAll(
            "#incidentTableBody tr"
        );


    rows.forEach(row => {

        const text =
            row.textContent.toLowerCase();


        const rowSeverity =
            row.dataset.severity;


        const rowStatus =
            row.dataset.status;


        const matchesSearch =
            text.includes(search);


        const matchesSeverity =
            severity === "ALL" ||
            rowSeverity === severity;


        const matchesStatus =
            status === "ALL" ||
            rowStatus === status;


        if (
            matchesSearch &&
            matchesSeverity &&
            matchesStatus
        ) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });

}


// ---------------------------------------------------------
// Resolve incident
// ---------------------------------------------------------

async function resolveIncident(id) {

    const confirmed =
        confirm(
            "Mark this incident as resolved?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `/api/incidents/${id}/resolve`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Unable to resolve incident."
            );

        }


        window.location.reload();


    } catch (error) {

        console.error(error);

        alert(
            "Unable to resolve incident."
        );

    }

}


// ---------------------------------------------------------
// Dashboard initialization
// ---------------------------------------------------------

document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "OpsWatch interface initialized."
        );

    }
);

// =========================================================
// INCIDENT SIMULATION
// =========================================================

async function simulateIncident(type) {

    const confirmed = confirm(
        "Generate a simulated " +
        type +
        " incident?"
    );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `/api/simulate/${type}`,
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Simulation failed."
            );

        }


        console.log(
            "Simulated incident:",
            data
        );


        window.location.reload();


    } catch (error) {

        console.error(error);

        alert(
            "Unable to generate simulated incident."
        );

    }

}

// =========================================================
// SERVICE MONITORING
// =========================================================

async function checkService(id) {

    try {

        const response =
            await fetch(
                `/api/services/${id}/check`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Service check failed."
            );

        }


        const data =
            await response.json();


        console.log(
            "Service result:",
            data
        );


        window.location.reload();

    }

    catch (error) {

        console.error(error);

        alert(
            "Unable to check service."
        );

    }
}


async function checkAllServices() {

    const buttons =
        document.querySelectorAll(
            ".check-button"
        );


    for (const button of buttons) {

        button.disabled = true;

    }


    try {

        const response =
            await fetch(
                "/api/services"
            );


        const services =
            await response.json();


        for (const service of services) {

            await fetch(
                `/api/services/${service.id}/check`,
                {
                    method: "POST"
                }
            );

        }


        window.location.reload();

    }

    catch (error) {

        console.error(error);

        alert(
            "Unable to check all services."
        );

    }

}