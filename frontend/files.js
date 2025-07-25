// files.js
// Este archivo contiene la lógica para mostrar archivos procesados
/**
 * Componente de Archivos JavaScript
 * Este archivo maneja la funcionalidad de la sección de archivos incluyendo:
 * - Carga de metadatos de archivos desde files.json
 * - Visualización de tarjetas de archivos con iconos apropiados
 * - Manejo de acciones de descarga/visualización
 */

/**
 * Inicializa el componente de archivos
 */
function initFiles() {
    // Cargar los datos de archivos
    cargarArchivos();
    
    console.log('Componente de archivos inicializado');
}

/**
 * Carga archivos desde el archivo JSON
 */
function cargarArchivos() {
    // Obtener archivos desde el JSON
    fetch('data/files.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cargar archivos');
            }
            return response.json();
        })
        .then(data => {
            // Mostrar los archivos
            mostrarArchivos(data);
        })
        .catch(error => {
            console.error('Error al cargar archivos:', error);
            
            // Mostrar notificación de error
            mostrarNotificacion('Error al cargar archivos. Por favor intente más tarde.', 'error');
            
            // Mostrar mensaje de error en el contenedor
            const contenedorArchivos = document.getElementById('files-container');
            if (contenedorArchivos) {
                contenedorArchivos.innerHTML = `
                    <div class="col-12 text-center">
                        <p class="text-danger">Error al cargar archivos. Por favor intente más tarde.</p>
                    </div>
                `;
            }
        });
}

/**
 * Muestra los archivos en el contenedor
 * @param {Array} archivos - Array de objetos de archivos
 */
function mostrarArchivos(archivos) {
    // Obtener el contenedor de archivos
    const contenedorArchivos = document.getElementById('files-container');
    if (!contenedorArchivos) {
        console.error('No se encontró el contenedor de archivos');
        return;
    }
    
    // Limpiar el contenedor
    contenedorArchivos.innerHTML = '';
    
    // Verificar si hay archivos
    if (!archivos || archivos.length === 0) {
        contenedorArchivos.innerHTML = `
            <div class="col-12 text-center">
                <p class="text-muted">No hay archivos disponibles</p>
            </div>
        `;
        return;
    }
    
    // Agregar CSS de Bootstrap Icons si no está incluido
    if (!document.querySelector('link[href*="bootstrap-icons"]')) {
        const iconsCss = document.createElement('link');
        iconsCss.rel = 'stylesheet';
        iconsCss.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css';
        document.head.appendChild(iconsCss);
    }
    
    // Mostrar los archivos
    archivos.forEach(archivo => {
        // Crear tarjeta para cada archivo
        const tarjetaArchivo = document.createElement('div');
        tarjetaArchivo.className = 'col-md-3 col-sm-6 mb-4';
        
        // Obtener extensión del archivo
        const extension = archivo.filename.split('.').pop().toLowerCase();
        
        // Obtener icono apropiado para el tipo de archivo
        const claseIcono = obtenerIconoArchivo(extension);
        
        // Formatear tamaño del archivo
        const tamañoFormateado = formatearTamañoArchivo(archivo.size);
        
        // Crear HTML de la tarjeta
        tarjetaArchivo.innerHTML = `
            <div class="card file-card text-center h-100">
                <div class="card-body">
                    <i class="bi ${claseIcono} file-icon"></i>
                    <h5 class="file-name">${archivo.filename}</h5>
                    <p class="file-type">${archivo.type}</p>
                    <p class="file-size">${tamañoFormateado}</p>
                    <a href="${archivo.url}" class="btn btn-sm btn-outline-primary" 
                       target="_blank" download="${archivo.filename}">
                        Descargar
                    </a>
                    ${esVisualizable(extension) ? 
                        `<a href="${archivo.url}" class="btn btn-sm btn-outline-secondary ms-2" 
                           target="_blank">Ver</a>` : ''}
                </div>
            </div>
        `;
        
        // Agregar evento click a la tarjeta (excluyendo botones)
        tarjetaArchivo.querySelector('.card').addEventListener('click', function(e) {
            // Solo activar si no se hizo click en un botón
            if (!e.target.closest('a.btn')) {
                // Mostrar detalles o descargar archivo
                manejarClickTarjetaArchivo(archivo);
            }
        });
        
        // Agregar tarjeta al contenedor
        contenedorArchivos.appendChild(tarjetaArchivo);
    });
}

/**
 * Maneja el click en una tarjeta de archivo
 * @param {Object} archivo - Objeto de archivo
 */
function manejarClickTarjetaArchivo(archivo) {
    // Obtener extensión del archivo
    const extension = archivo.filename.split('.').pop().toLowerCase();
    
    // Si el archivo es visualizable, abrirlo en nueva pestaña
    if (esVisualizable(extension)) {
        window.open(archivo.url, '_blank');
    } else {
        // De lo contrario, iniciar descarga
        const link = document.createElement('a');
        link.href = archivo.url;
        link.download = archivo.filename;
        link.click();
    }
}

/**
 * Verifica si un archivo puede visualizarse en el navegador
 * @param {string} extension - Extensión del archivo
 * @returns {boolean} Indica si el archivo es visualizable
 */
function esVisualizable(extension) {
    // Lista de extensiones que pueden verse en el navegador
    const extensionesVisualizables = [
        'pdf', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'txt', 'html', 'htm', 'mp4', 'webm', 'mp3', 'wav'
    ];
    
    return extensionesVisualizables.includes(extension.toLowerCase());
}

/**
 * Obtiene el icono correspondiente a un tipo de archivo
 * @param {string} extension - Extensión del archivo
 * @returns {string} Clase CSS del icono
 */
function obtenerIconoArchivo(extension) {
    const iconos = {
        'pdf': 'bi-file-earmark-pdf',
        'doc': 'bi-file-earmark-word',
        'docx': 'bi-file-earmark-word',
        'xls': 'bi-file-earmark-excel',
        'xlsx': 'bi-file-earmark-excel',
        'ppt': 'bi-file-earmark-ppt',
        'pptx': 'bi-file-earmark-ppt',
        'jpg': 'bi-file-image',
        'jpeg': 'bi-file-image',
        'png': 'bi-file-image',
        'gif': 'bi-file-image',
        'svg': 'bi-file-image',
        'mp3': 'bi-file-music',
        'wav': 'bi-file-music',
        'mp4': 'bi-file-play',
        'webm': 'bi-file-play',
        'zip': 'bi-file-zip',
        'rar': 'bi-file-zip',
        'txt': 'bi-file-text',
        'html': 'bi-file-code',
        'htm': 'bi-file-code',
        'js': 'bi-file-code',
        'json': 'bi-file-code',
        'css': 'bi-file-code'
    };
    
    return iconos[extension] || 'bi-file-earmark';
}

/**
 * Formatea el tamaño del archivo para mostrarlo legiblemente
 * @param {number} bytes - Tamaño en bytes
 * @returns {string} Tamaño formateado
 */
function formatearTamañoArchivo(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Muestra una notificación al usuario
 * @param {string} mensaje - Texto a mostrar
 * @param {string} tipo - Tipo de notificación (success, error, warning, info)
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Implementación básica - en producción usar librería como Toastr
    console.log(`Notificación [${tipo}]: ${mensaje}`);
    alert(`[${tipo.toUpperCase()}] ${mensaje}`);
}

// Exportar funciones si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initFiles,
        cargarArchivos,
        mostrarArchivos
    };
}