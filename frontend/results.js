/**
 * Componente de Resultados JavaScript
 * Este archivo maneja la funcionalidad del bloque de resultados incluyendo:
 * - Carga de resultados desde results.json
 * - Implementación de paginación
 * - Actualización del número de elementos por página
 */

// Variables de estado para resultados
let datosResultados = [];
let paginaActual = 1;
let elementosPorPagina = 10;
let paginasTotales = 0;

/**
 * Inicializa el componente de resultados
 */
function initResults() {
    // Cargar los datos de resultados
    cargarResultados();
    
    // Configurar listeners para la paginación
    configurarListenersPaginacion();
    
    console.log('Componente de resultados inicializado');
}

/**
 * Carga resultados desde el archivo JSON
 */
function cargarResultados() {
    // Obtener resultados desde el archivo JSON
    fetch('data/results.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cargar resultados');
            }
            return response.json();
        })
        .then(data => {
            // Almacenar los datos de resultados
            datosResultados = data;
            
            // Calcular el total de páginas
            paginasTotales = Math.ceil(datosResultados.length / elementosPorPagina);
            
            // Mostrar la primera página de resultados
            mostrarResultados(1);
            
            // Actualizar controles de paginación
            actualizarControlesPaginacion();
        })
        .catch(error => {
            console.error('Error al cargar resultados:', error);
            
            // Mostrar notificación de error
            mostrarNotificacion('Error al cargar resultados. Por favor intente más tarde.', 'error');
            
            // Mostrar mensaje de error en el contenedor
            const contenedorResultados = document.getElementById('results-container');
            if (contenedorResultados) {
                contenedorResultados.innerHTML = `
                    <div class="col-12 text-center">
                        <p class="text-danger">Error al cargar resultados. Por favor intente más tarde.</p>
                    </div>
                `;
            }
        });
}

/**
 * Muestra una página específica de resultados
 * @param {number} pagina - El número de página a mostrar
 */
function mostrarResultados(pagina) {
    // Validar el número de página
    if (pagina < 1 || pagina > paginasTotales) {
        console.error('Número de página inválido:', pagina);
        return;
    }
    // Actualizar página actual
    paginaActual = pagina;
    // Calcular índices de inicio y fin para la página actual
    const indiceInicio = (pagina - 1) * elementosPorPagina;
    const indiceFin = Math.min(indiceInicio + elementosPorPagina, datosResultados.length);
    // Obtener los resultados de la página actual
    const resultadosActuales = datosResultados.slice(indiceInicio, indiceFin);
    // Obtener el contenedor de resultados
    const contenedorResultados = document.getElementById('results-container');
    if (!contenedorResultados) {
        console.error('Contenedor de resultados no encontrado');
        return;
    }
    // Limpiar el contenedor
    contenedorResultados.innerHTML = '';
    // Mostrar los resultados
    resultadosActuales.forEach(resultado => {
        // Compatibilidad con campos antiguos y nuevos
        const title = resultado.title || resultado.titulo || "Sin título";
        const category = resultado.category || resultado.categoria || "Sin categoría";
        const description = resultado.description || resultado.descripcion || "Sin descripción";
        const date = resultado.date || resultado.fecha || "";
        // Crear tarjeta para cada resultado
        const tarjetaResultado = document.createElement('div');
        tarjetaResultado.className = 'col-md-6 col-lg-4';
        tarjetaResultado.innerHTML = `
            <div class="card result-card">
                <div class="card-body">
                    <h5 class="card-title">${title}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">${category}</h6>
                    <p class="card-text">${description}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${formatearFecha(date)}</small>
                        <a href="#" class="btn btn-sm btn-primary">Ver Detalles</a>
                    </div>
                </div>
            </div>
        `;
        // Agregar tarjeta al contenedor
        contenedorResultados.appendChild(tarjetaResultado);
    });
    // Actualizar controles de paginación
    actualizarControlesPaginacion();
}

/**
 * Actualiza los controles de paginación según el estado actual
 */
function actualizarControlesPaginacion() {
    // Obtener el contenedor de paginación
    const paginacion = document.getElementById('pagination');
    if (!paginacion) {
        console.error('Contenedor de paginación no encontrado');
        return;
    }
    
    // Obtener la lista de paginación
    const listaPaginacion = paginacion.querySelector('ul.pagination');
    if (!listaPaginacion) {
        console.error('Lista de paginación no encontrada');
        return;
    }
    
    // Limpiar la lista excepto los botones Anterior y Siguiente
    const botonAnterior = document.getElementById('prev-page');
    const botonSiguiente = document.getElementById('next-page');
    
    // Eliminar todos los botones de número de página
    Array.from(listaPaginacion.children).forEach(item => {
        if (!item.id.includes('prev-page') && !item.id.includes('next-page')) {
            listaPaginacion.removeChild(item);
        }
    });
    
    // Agregar botones de número de página
    for (let i = 1; i <= paginasTotales; i++) {
        const itemPagina = document.createElement('li');
        itemPagina.className = `page-item ${i === paginaActual ? 'active' : ''}`;
        itemPagina.id = `page-${i}`;
        itemPagina.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        
        // Agregar listener para el evento click
        itemPagina.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarResultados(i);
        });
        
        // Insertar antes del botón Siguiente
        listaPaginacion.insertBefore(itemPagina, botonSiguiente);
    }
    
    // Actualizar estado del botón Anterior
    if (botonAnterior) {
        if (paginaActual === 1) {
            botonAnterior.classList.add('disabled');
        } else {
            botonAnterior.classList.remove('disabled');
        }
    }
    
    // Actualizar estado del botón Siguiente
    if (botonSiguiente) {
        if (paginaActual === paginasTotales) {
            botonSiguiente.classList.add('disabled');
        } else {
            botonSiguiente.classList.remove('disabled');
        }
    }
}

/**
 * Configura los listeners para los controles de paginación
 */
function configurarListenersPaginacion() {
    // Evento click para botón Anterior
    const botonAnterior = document.getElementById('prev-page');
    if (botonAnterior) {
        botonAnterior.addEventListener('click', function(e) {
            e.preventDefault();
            if (paginaActual > 1) {
                mostrarResultados(paginaActual - 1);
            }
        });
    }
    
    // Evento click para botón Siguiente
    const botonSiguiente = document.getElementById('next-page');
    if (botonSiguiente) {
        botonSiguiente.addEventListener('click', function(e) {
            e.preventDefault();
            if (paginaActual < paginasTotales) {
                mostrarResultados(paginaActual + 1);
            }
        });
    }
}

/**
 * Actualiza el número de elementos por página
 * @param {number} nuevosElementosPorPagina - El nuevo número de elementos por página
 */
function actualizarElementosPorPagina(nuevosElementosPorPagina) {
    // Actualizar elementos por página
    elementosPorPagina = nuevosElementosPorPagina;
    
    // Recalcular total de páginas
    paginasTotales = Math.ceil(datosResultados.length / elementosPorPagina);
    
    // Ajustar página actual si es necesario
    if (paginaActual > paginasTotales) {
        paginaActual = paginasTotales;
    }
    
    // Mostrar la página actual con los nuevos elementos por página
    mostrarResultados(paginaActual);
}