const PROGRAM_ORDER = [
    "After Effects",
    "Nuke",
    "Maya",
    "3D Max",
    "Houdini",
    "Unreal",
    "Cinema4D",
    "Boujou",
    "PF Track",
    "3D Equalizer",
    "Photoshop",
    "Illustrator",
    "Substance"
];

// Función para cargar los inputs dinámicos de los programas
function generarInputs() {
    const container = document.getElementById("programas-container");
    container.innerHTML = ""; // Asegura que no se dupliquen elementos

    PROGRAM_ORDER.forEach(programa => {
        const div = document.createElement("div");
        div.classList.add("config-item");

        const label = document.createElement("label");
        label.textContent = programa + ":";

        const input = document.createElement("input");
        input.type = "text";
        input.id = `ruta-${programa.replace(/\s+/g, '-').toLowerCase()}`;
        input.readOnly = true;

        const button = document.createElement("button");
        button.textContent = "Seleccionar Archivo";
        button.onclick = () => seleccionarRuta(programa);

        div.appendChild(label);
        div.appendChild(input);
        div.appendChild(button);
        container.appendChild(div);
    });

    cargarConfiguracion(); // Cargar configuración después de generar los inputs
}

function seleccionarRuta(tipo) {
    fetch(`/seleccionar-ruta`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tipo: tipo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.ruta) {
            if (tipo === "proyecto") {
                document.getElementById("proyecto-path").value = data.ruta;
            } else {
                const inputId = `ruta-${tipo.replace(/\s+/g, '-').toLowerCase()}`;
                document.getElementById(inputId).value = data.ruta;
            }
            guardarConfiguracion();  // Guardar automáticamente
        }
    })
    .catch(error => console.error("Error seleccionando ruta:", error));
}

function guardarConfiguracion() {
    const proyectoPath = document.getElementById("proyecto-path").value;
    const programas = {};

    PROGRAM_ORDER.forEach(programa => {
        const inputId = `ruta-${programa.replace(/\s+/g, '-').toLowerCase()}`;
        programas[programa] = document.getElementById(inputId).value;
    });

    const configData = { proyecto: proyectoPath, programas: programas };

    console.log(">>> Enviando configuración al servidor:", configData);  // Debug

    fetch("/guardar-configuracion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(configData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(">>> Respuesta del servidor:", data);
        if (data.status === "success") {
            console.log(">>> Configuración guardada correctamente.");
        } else {
            console.error(">>> Error al guardar configuración:", data.message);
        }
    })
    .catch(error => console.error("Error guardando configuración:", error));
}

// Cargar configuración desde Flask
function cargarConfiguracion() {
    fetch("/cargar-configuracion")
        .then(response => response.json())
        .then(data => {
            console.log(">>> Configuración cargada desde el servidor:", data);

            if (data.proyecto) {
                document.getElementById("proyecto-path").value = data.proyecto;
            }

            if (data.programas) {
                PROGRAM_ORDER.forEach(programa => {
                    const inputId = `ruta-${programa.replace(/\s+/g, '-').toLowerCase()}`;
                    if (data.programas[programa]) {
                        document.getElementById(inputId).value = data.programas[programa];
                    }
                });
            }
        })
        .catch(error => console.error("Error cargando configuración:", error));
}

// Al cargar la página, generamos los inputs y luego cargamos la configuración guardada
document.addEventListener("DOMContentLoaded", generarInputs);