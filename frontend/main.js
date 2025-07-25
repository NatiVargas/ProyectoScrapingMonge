/**
 * Archivo principal JavaScript para el Panel de Control Moderno
 * Este archivo inicializa la aplicación y maneja funcionalidades comunes
 */

// Esperar a que el DOM esté completamente cargado antes de ejecutar cualquier JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Aplicación inicializada');
    // Inicializar todos los componentes
    initCalendar();
    initResults();
    initFiles();
    
    // Agregar listeners para interacciones de UI
    agregarEventListeners();
});

/**
 * Agrega listeners para interacciones de la interfaz
 */
function agregarEventListeners() {
    // Evento de cambio en el selector de elementos por página
    const selectorElementosPorPagina = document.getElementById('items-per-page');
    if (selectorElementosPorPagina) {
        selectorElementosPorPagina.addEventListener('change', function() {
            // Actualizar el número de elementos por página y refrescar resultados
            const elementosPorPagina = parseInt(this.value);
            actualizarElementosPorPagina(elementosPorPagina);
        });
    }
}

/**
 * Muestra un mensaje de notificación al usuario
 * @param {string} mensaje - El mensaje a mostrar
 * @param {string} tipo - El tipo de mensaje (success, error, info, warning)
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Podrías implementar un sistema de notificaciones toast aquí
    console.log(`${tipo.toUpperCase()}: ${mensaje}`);
    
    // Por ahora usaremos un alert por simplicidad
    alert(mensaje);
}

/**
 * Formatea una fecha para mostrarla
 * @param {Date} fecha - La fecha a formatear
 * @param {boolean} incluirHora - Si incluir la hora
 * @returns {string} La cadena de fecha formateada
 */
function formatearFecha(fecha, incluirHora = false) {
    if (!(fecha instanceof Date)) {
        fecha = new Date(fecha);
    }
    
    const opciones = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric'
    };
    
    if (incluirHora) {
        opciones.hour = '2-digit';
        opciones.minute = '2-digit';
    }
    
    return fecha.toLocaleDateString('es-ES', opciones);
}

/**
 * Formatea un tamaño de archivo para mostrarlo
 * @param {number} bytes - El tamaño del archivo en bytes
 * @returns {string} El tamaño de archivo formateado
 */
function formatearTamanoArchivo(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const unidades = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + unidades[i];
}

/**
 * Obtiene el icono apropiado para un tipo de archivo
 * @param {string} tipoArchivo - El tipo/extensión del archivo
 * @returns {string} La clase del icono
 */
function obtenerIconoArchivo(tipoArchivo) {
    // Mapeo de extensiones a iconos de Bootstrap
    const mapeoIconos = {
        'pdf': 'bi-file-earmark-pdf',
        'doc': 'bi-file-earmark-word',
        'docx': 'bi-file-earmark-word',
        'xls': 'bi-file-earmark-excel',
        'xlsx': 'bi-file-earmark-excel',
        'ppt': 'bi-file-earmark-ppt',
        'pptx': 'bi-file-earmark-ppt',
        'txt': 'bi-file-earmark-text',
        'zip': 'bi-file-earmark-zip',
        'jpg': 'bi-file-earmark-image',
        'jpeg': 'bi-file-earmark-image',
        'png': 'bi-file-earmark-image',
        'gif': 'bi-file-earmark-image',
        'mp3': 'bi-file-earmark-music',
        'mp4': 'bi-file-earmark-play',
        'csv': 'bi-file-earmark-spreadsheet',
        'json': 'bi-file-earmark-code'
    };
    
    // Obtener la extensión del archivo (en minúsculas)
    const extension = tipoArchivo.toLowerCase();
    
    // Devolver la clase del icono correspondiente o uno por defecto si no se encuentra
    return mapeoIconos[extension] || 'bi-file-earmark';
}

/**
 * Actualiza el número de elementos mostrados por página
 * @param {number} cantidad - Número de elementos por página
 */
function actualizarElementosPorPagina(cantidad) {
    console.log(`Mostrando ${cantidad} elementos por página`);
    // Aquí iría la lógica para actualizar la visualización
    // Por ahora solo mostramos una notificación
    mostrarNotificacion(`Configuración cambiada: mostrando ${cantidad} elementos por página`, 'info');
}

// Exportar funciones si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        mostrarNotificacion,
        formatearFecha,
        formatearTamanoArchivo,
        obtenerIconoArchivo
    };
}