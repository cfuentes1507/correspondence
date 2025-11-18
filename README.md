# Correspondencia

Módulo de gestión de correspondencia institucional para Odoo 15.

## Resumen

Este módulo tiene como objetivo digitalizar y centralizar el proceso de envío, recepción, seguimiento y archivo de documentos y comunicados internos entre los diferentes departamentos de una organización.

## Funcionalidades Principales

*   **Gestión de Documentos:** Creación y seguimiento de correspondencia con campos como Correlativo, Asunto, Fecha, Autor y Departamento Destinatario.
*   **Flujo de Trabajo:** Un ciclo de vida claro para cada documento: `Borrador` -> `Firmado` -> `Enviado` -> `Respondido`.
*   **Estructura Organizacional:** Permite configurar Departamentos y Tipos de Correspondencia para una mejor clasificación.
*   **Trazabilidad:** Capacidad de responder a un documento, creando un hilo de conversación.
*   **Integración con Odoo:** Utiliza el sistema de chatter de Odoo para notificaciones y seguimiento de actividades.
*   **Reportes Dinámicos:** Asocia plantillas de reportes personalizadas a cada tipo de correspondencia.
*   **Gestión de Directores:** Mantiene un historial de los directores de cada departamento, calculando automáticamente el director actual.
*   **Auditoria Rapida a los Documentos:** Cada documento de Correspondencia se genera con un codigo QR unico que permite trazar en cualquiero lugar la validez del documento.
*   **Envio de Adjuntos Mediante Vistas Publicas:** Mediante el uso de la vista publica se pueden enviar archivos, los cuales solo pueden ser descargados si se cuenta con un usuario autorizado.

## Estructura del Módulo

### Modelos de Datos

*   `correspondence_document`: El modelo central que representa cada documento de correspondencia. Gestiona el estado, los adjuntos, y las relaciones entre documentos (respuestas).
*   `correspondence_department`: Define los departamentos de la organización. Cada usuario está asociado a un departamento.
*   `correspondence_type`: Permite catalogar los documentos (Ej: Memorando, Circular, Oficio) y asociarles una acción de reporte específica.
*   `correspondence.department.director`: Almacena el historial de directores por departamento, evitando solapamientos de fechas.
*   `correspondence.document.read_status`: Registra qué departamento ha leído un documento y cuándo, proporcionando un acuse de recibo.

### Flujo de Trabajo del Documento

1.  **Borrador (`draft`):** El documento es creado por un usuario. Solo él puede verlo y editarlo.
2.  **Firmado (`signed`):** El autor sube una versión firmada del documento. El contenido principal ya no es editable.
3.  **Enviado (`sent`):** El documento se envía a los departamentos destinatarios. Aparece en su "Bandeja de Entrada".
4.  **Leído:** Cuando un miembro de un departamento destinatario abre el documento, se registra un estado de lectura para ese departamento.
5.  **Respondido (`replied`):** Si un destinatario responde al documento, se crea un nuevo documento enlazado y el estado del documento original cambia a "Respondido".

### Menús y Vistas

*   **Bandeja de Entrada:** Muestra la correspondencia recibida pendiente de acción.
*   **Bandeja de Salida:** Muestra la correspondencia enviada por el usuario actual.
*   **Archivo:** Un repositorio completo de toda la correspondencia, con potentes filtros de búsqueda.
*   **Configuración:**
    *   **Departamentos:** Para crear y gestionar los departamentos de la organización.
    *   **Tipos de Correspondencia:** Para definir las categorías de documentos y sus reportes asociados.

## Instalación

1.  Clona o descarga este repositorio.
2.  Añade la carpeta `correspondence` a tu directorio de `addons` de Odoo.
3.  Reinicia el servicio de Odoo.
4.  Activa el modo desarrollador en Odoo.
5.  Ve a `Aplicaciones`, busca "Correspondencia Institucional" e instálalo.

<img width="781" height="481" alt="Diagrama de Flujo drawio" src="https://github.com/user-attachments/assets/f7cec1d8-ccfe-4a1a-ad0e-9b6a49e90c7a" />
