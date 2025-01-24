document.addEventListener("DOMContentLoaded", function() {
    let selectProyecto = document.getElementById("proyecto-select");
    let selectPlano = document.getElementById("plano-select");
    let programasContainer = document.getElementById("programas-container");


    function limpiarCombos() {
        selectProyecto.innerHTML = "<option>Seleccione un proyecto...</option>";
        selectPlano.innerHTML = "<option>Seleccione un proyecto...</option>";
    }

    function cargarProyectos() {
        fetch('/proyectos')
            .then(response => response.json())
            .then(data => {
                return fetch('/proyecto_seleccionado')
                    .then(response => response.json())
                    .then(proyectoSeleccionado => ({ data, proyectoSeleccionado }));
            })
            .then(({ data, proyectoSeleccionado }) => {
                selectProyecto.innerHTML = "";

                if (data.length === 0) {
                    limpiarCombos();
                    return;
                }

                data.forEach(proyecto => {
                    let option = document.createElement("option");
                    option.textContent = proyecto.nombre;
                    option.value = proyecto.nombre;
                    selectProyecto.appendChild(option);
                });

                // Seleccionar automáticamente el primer proyecto disponible
                let primerProyecto = data[0].nombre;
                selectProyecto.value = primerProyecto;

                // Cargar planos del primer proyecto automáticamente
                cargarPlanos(primerProyecto, "Assets");

                // Si ya había un proyecto guardado, seleccionarlo en lugar del primero
                if (proyectoSeleccionado.nombre) {
                    selectProyecto.value = proyectoSeleccionado.nombre;
                    cargarPlanos(proyectoSeleccionado.nombre, proyectoSeleccionado.plano.nombre);
                }
            })
            .catch(error => console.error("Error cargando proyectos:", error));
    }

    selectProyecto.addEventListener("change", function() {
        let nombreProyecto = this.value;
        if (!nombreProyecto) {
            limpiarCombos();
            return;
        }

        fetch('/proyecto_seleccionado', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre: nombreProyecto, plano: "Assets" })
        })
        .then(() => cargarPlanos(nombreProyecto, "Assets"));
    });

    function cargarPlanos(proyecto, planoSeleccionado = "Assets") {
        fetch(`/planos/${proyecto}`)
            .then(response => response.json())
            .then(planos => {
                selectPlano.innerHTML = "";

                if (planos.length === 0) {
                    selectPlano.innerHTML = "<option>Seleccione un proyecto...</option>";
                    return;
                }

                let optionAssets = document.createElement("option");
                optionAssets.textContent = "Assets";
                optionAssets.value = "Assets";
                selectPlano.appendChild(optionAssets);

                planos.forEach(plano => {
                    if (plano.nombre !== "Assets") {
                        let option = document.createElement("option");
                        option.textContent = plano.nombre.replace(/^[a-zA-Z]+_/, ""); 
                        option.value = plano.nombre;
                        selectPlano.appendChild(option);
                    }
                });

                selectPlano.value = planoSeleccionado;
            })
            .catch(error => console.error("Error cargando planos:", error));
    }

    selectPlano.addEventListener("change", function() {
        let planoSeleccionado = this.value;
        let proyectoSeleccionado = selectProyecto.value;

        if (planoSeleccionado && proyectoSeleccionado) {
            fetch('/proyecto_seleccionado', {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nombre: proyectoSeleccionado, plano: planoSeleccionado })
            })
            .then(response => response.json())
            .then(data => console.log(">>> Respuesta del servidor:", data))
            .catch(error => console.error("Error al guardar el plano:", error));
        }
    });


    function cargarProgramas() {
        fetch('/programas')
            .then(response => response.json())
            .then(programas => {
                programasContainer.innerHTML = "";
                programas.forEach(programa => {
                    let boton = document.createElement("button");
                    let img = document.createElement("img");

                    // Convertir el nombre del programa en formato compatible con el archivo de icono
                    let iconoNombre = programa.nombre.toLowerCase().replace(/ /g, "_") + ".png";

                    img.src = `static/icons/${iconoNombre}`;
                    img.alt = programa.nombre;
                    img.classList.add("icono-programa");

                    boton.appendChild(img);
                    boton.classList.add("programa-button");
                    boton.setAttribute("title", programa.nombre); // Tooltip con el nombre del programa

                    boton.addEventListener("click", function() {
                        abrirPrograma(programa.nombre);
                    });

                    programasContainer.appendChild(boton);
                });
            })
            .catch(error => console.error("Error cargando programas:", error));
    }

    function abrirPrograma(nombrePrograma) {
        let proyecto = document.getElementById("proyecto-select").value;
        let plano = document.getElementById("plano-select").value;

        if (!proyecto || !plano) {
            alert("Selecciona un proyecto y un plano antes de abrir un programa.");
            return;
        }

        fetch('/abrir-programa', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ proyecto, plano, programa: nombrePrograma })
        }).then(response => response.json())
          .then(data => console.log("Programa abierto:", data))
          .catch(error => console.error("Error al abrir programa:", error));
    }

    cargarProyectos();  // Cargar proyectos al inicio
    cargarProgramas();

});