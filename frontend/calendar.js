/**
 * Componente de Calendario JavaScript
 * Este archivo maneja la funcionalidad completa del calendario incluyendo:
 * - Inicialización del calendario
 * - Carga y visualización de eventos
 * - Manejo de interacciones del usuario
 * - Mostrar detalles de eventos
 */

// Variable para almacenar la instancia del calendario
let calendar;

/**
 * Inicializa el calendario cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', function() {
    initCalendar();
});

/**
 * Función principal para inicializar el calendario
 */
function initCalendar() {
    // Obtener el elemento contenedor del calendario
    const calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) {
        console.error('Error: No se encontró el elemento con ID "calendar"');
        showNotification('No se pudo inicializar el calendario. Elemento no encontrado.', 'error');
        return;
    }
    
    try {
        // Configuración del calendario
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es', // Configuración regional en español
            headerToolbar: {
                left: 'prev,next hoy',
                center: 'titulo',
                right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
            },
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                day: 'Día',
                list: 'Lista'
            },
            selectable: true,
            selectMirror: true,
            dayMaxEvents: true,
            weekNumbers: true,
            weekNumberTitle: 'Sem',
            navLinks: true,
            
            // Manejo de eventos
            eventClick: handleEventClick,
            select: handleDateSelect,
            
            // Fuente de datos de eventos
            events: loadCalendarEvents,
            
            // Textos personalizados
            allDayText: 'Todo el día',
            noEventsText: 'No hay eventos para mostrar'
        });
        
        // Renderizar el calendario
        calendar.render();
        console.log('Calendario inicializado correctamente');
        
    } catch (error) {
        console.error('Error al inicializar el calendario:', error);
        showNotification('Error al cargar el calendario. Por favor recarga la página.', 'error');
    }
}

/**
 * Carga los eventos del calendario desde un archivo JSON
 * @param {Object} info - Información sobre el rango de fechas actual
 * @param {Function} successCallback - Función para devolver los eventos cargados
 * @param {Function} failureCallback - Función para manejar errores
 */
function loadCalendarEvents(info, successCallback, failureCallback) {
    console.log('Cargando eventos para:', info.startStr, 'a', info.endStr);
    
    fetch('data/events.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la red al cargar eventos');
            }
            return response.json();
        })
        .then(data => {
            // Procesar y formatear los eventos
            const eventosFormateados = data.map(evento => ({
                id: evento.id || generarIdUnico(),
                title: evento.titulo || 'Evento sin título',
                start: evento.inicio || new Date(),
                end: evento.fin || null,
                allDay: evento.todoElDia || false,
                color: evento.color || getEventColor(evento.categoria),
                extendedProps: {
                    descripcion: evento.descripcion || 'No hay descripción disponible',
                    ubicacion: evento.ubicacion || 'Ubicación no especificada',
                    categoria: evento.categoria || 'general',
                    participantes: evento.participantes || []
                }
            }));
            
            successCallback(eventosFormateados);
            console.log('Eventos cargados correctamente:', eventosFormateados.length);
        })
        .catch(error => {
            console.error('Error al cargar eventos:', error);
            failureCallback(error);
            showNotification('No se pudieron cargar los eventos. Intente nuevamente más tarde.', 'error');
        });
}

/**
 * Maneja el clic en un evento para mostrar sus detalles
 * @param {Object} info - Información del evento clickeado
 */
function handleEventClick(info) {
    const evento = info.event;
    const modal = document.getElementById('eventoModal');
    
    if (!modal) {
        console.warn('Modal no encontrado, mostrando detalles en consola');
        console.log('Detalles del evento:', evento.toPlainObject());
        return;
    }

    // Formatear fechas
    const fechaInicio = formatFecha(evento.start, true);
    const fechaFin = evento.end ? formatFecha(evento.end, true) : null;
    const esTodoElDia = evento.allDay ? 'Sí' : 'No';

    // Construir lista de participantes
    const participantes = evento.extendedProps.participantes || [];
    const listaParticipantes = participantes.length > 0 
        ? participantes.map(p => `<li>${p.nombre} (${p.rol})</li>`).join('') 
        : '<li>No hay participantes registrados</li>';

    // Llenar el modal con la información del evento
    modal.querySelector('.modal-title').textContent = evento.title;
    modal.querySelector('.evento-fecha-inicio').textContent = fechaInicio;
    modal.querySelector('.evento-fecha-fin').textContent = fechaFin || 'No especificado';
    modal.querySelector('.evento-todo-el-dia').textContent = esTodoElDia;
    modal.querySelector('.evento-ubicacion').textContent = evento.extendedProps.ubicacion;
    modal.querySelector('.evento-categoria').textContent = evento.extendedProps.categoria;
    modal.querySelector('.evento-descripcion').innerHTML = evento.extendedProps.descripcion;
    modal.querySelector('.evento-participantes').innerHTML = listaParticipantes;
    
    // Mostrar el modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

/**
 * Maneja la selección de un rango de fechas
 * @param {Object} info - Información sobre las fechas seleccionadas
 */
function handleDateSelect(info) {
    const modal = document.getElementById('nuevoEventoModal');
    
    if (!modal) {
        console.log('Selección de fechas:', info.startStr, 'a', info.endStr);
        return;
    }

    // Configurar los campos de fecha en el formulario de nuevo evento
    modal.querySelector('#eventoInicio').value = info.startStr;
    modal.querySelector('#eventoFin').value = info.endStr;
    
    // Mostrar el modal para crear nuevo evento
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    // Limpiar la selección en el calendario
    calendar.unselect();
}

/**
 * Genera un color basado en la categoría del evento
 * @param {String} categoria - Categoría del evento
 * @returns {String} Código hexadecimal de color
 */
function getEventColor(categoria) {
    const colores = {
        'reunion': '#4285F4',     // Azul
        'feriado': '#34A853',     // Verde
        'importante': '#EA4335',   // Rojo
        'personal': '#FBBC05',    // Amarillo
        'conferencia': '#9C27B0', // Morado
        'taller': '#00ACC1',      // Cian
        'entrega': '#FF6D00',     // Naranja
        'general': '#757575'       // Gris
    };
    
    return colores[categoria.toLowerCase()] || colores.general;
}

/**
 * Formatea una fecha para mostrarla al usuario
 * @param {Date} fecha - Objeto de fecha a formatear
 * @param {Boolean} incluirHora - Indica si incluir la hora en el formato
 * @returns {String} Fecha formateada
 */
function formatFecha(fecha, incluirHora = false) {
    if (!fecha) return 'Fecha no especificada';
    
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
 * Muestra una notificación al usuario
 * @param {String} mensaje - Texto a mostrar
 * @param {String} tipo - Tipo de notificación (success, error, warning, info)
 */
function showNotification(mensaje, tipo = 'info') {
    // Implementación básica - en un proyecto real podrías usar Toastr, SweetAlert, etc.
    console.log(`Notificación [${tipo}]: ${mensaje}`);
    alert(`[${tipo.toUpperCase()}] ${mensaje}`);
}

/**
 * Genera un ID único para nuevos eventos
 * @returns {String} ID único
 */
function generarIdUnico() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Exportar funciones para su uso en otros archivos si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initCalendar,
        loadCalendarEvents,
        handleEventClick,
        handleDateSelect
    };
}