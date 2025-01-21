document.addEventListener("DOMContentLoaded", function() {
    let selectProyecto = document.getElementById("proyecto-select");
    let selectPlano = document.getElementById("plano-select");

    function limpiarComboPlanos() {
        selectPlano.innerHTML = "";
    }

    // Cargar proyectos desde el backend
    fetch('/proyectos')
        .then(response => response.json())
        .then(data => {
            fetch('/proyecto_seleccionado')
                .then(response => response.json())
                .then(proyectoSeleccionado => {
                    let proyectoGuardado = proyectoSeleccionado.nombre || "";

                    selectProyecto.innerHTML = "";

                    if (!proyectoGuardado) {
                        let optionDefault = document.createElement("option");
                        optionDefault.textContent = "Seleccione un proyecto...";
                        optionDefault.value = "";
                        selectProyecto.appendChild(optionDefault);
                    }

                    data.forEach(proyecto => {
                        let option = document.createElement("option");
                        option.textContent = proyecto.nombre;
                        option.value = proyecto.nombre;
                        selectProyecto.appendChild(option);
                    });

                    if (proyectoGuardado) {
                        selectProyecto.value = proyectoGuardado;
                        cargarPlanos(proyectoGuardado, proyectoSeleccionado.plano.nombre);
                    }
                });
        });

    selectProyecto.addEventListener("change", function() {
        let nombreProyecto = this.value;
        limpiarComboPlanos();

        if (nombreProyecto) {
            fetch('/proyecto_seleccionado', {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nombre: nombreProyecto, plano: "Assets" })
            })
            .then(() => cargarPlanos(nombreProyecto, "Assets"));
        }
    });

    function cargarPlanos(proyecto, planoSeleccionado = "Assets") {
        fetch(`/planos/${proyecto}`)
            .then(response => response.json())
            .then(planos => {
                limpiarComboPlanos();
    
                planos.forEach(plano => {
                    let option = document.createElement("option");
                    option.textContent = plano.nombre.replace(/^[a-zA-Z]+_/, ""); 
                    option.value = plano.nombre;
                    selectPlano.appendChild(option);
                });
    
                // Si hay un plano guardado, seleccionarlo en el combo
                if (planoSeleccionado) {
                    selectPlano.value = planoSeleccionado;
                }
            });
    }

    selectPlano.addEventListener("change", function() {
        let planoSeleccionado = this.value;
        let proyectoSeleccionado = document.getElementById("proyecto-select").value;
    
        console.log(">>> Plano Seleccionado:", planoSeleccionado);  // Debug en consola
    
        if (planoSeleccionado && proyectoSeleccionado) {
            fetch('/proyecto_seleccionado', {  // Asegurar que se usa la ruta correcta
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nombre: proyectoSeleccionado, plano: planoSeleccionado })
            })
            .then(response => response.json())
            .then(data => console.log(">>> Respuesta del servidor:", data))
            .catch(error => console.error("Error al guardar el plano:", error));
        }
    });
});