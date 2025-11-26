# Correspondencia

Módulo de gestión de correspondencia institucional para Odoo 15.

## Resumen

Este módulo tiene como objetivo digitalizar y centralizar el proceso de envío, recepción, seguimiento y archivo de documentos y comunicados internos entre los diferentes departamentos de una organización.

## Funcionalidades Principales

*   **Gestión de Documentos:** Creación y seguimiento de correspondencia con campos como Correlativo, Asunto, Fecha, y adjuntos.
*   **Flujos de Trabajo Diferenciados:** Soporta tres flujos de correspondencia distintos: **Interno**, **Entrante** y **Saliente**, cada uno con su propio ciclo de vida y estados.
*   **Estructura Organizacional:** Se integra con el módulo de RRHH de Odoo, extendiendo los Departamentos (`hr.department`) para gestionar prefijos de correlativos, historial de directores y la capacidad de recibir correspondencia.
*   **Trazabilidad:** Capacidad de responder a un documento, creando un nuevo documento enlazado que mantiene el hilo de la conversación.
*   **Integración con Odoo:** Utiliza el sistema de chatter de Odoo para notificaciones y seguimiento de actividades.
*   **Reportes Dinámicos:** Asocia plantillas de reportes QWeb personalizadas a cada tipo de correspondencia (Memorando, Circular, Oficio, etc.).
*   **Gestión de Directores:** Mantiene un historial de los directores de cada departamento, utilizando automáticamente al director actual para la firma de documentos.
*   **Auditoría Rápida con Código QR:** Cada documento PDF generado incluye un código QR único que enlaza a una página pública para verificar la validez y los detalles del documento.
*   **Descarga Segura de Adjuntos:** La página pública permite visualizar los detalles del documento, pero restringe la descarga de archivos adjuntos solo a usuarios autenticados en el sistema.

## Estructura del Módulo

### Modelos de Datos

*   `correspondence_document`: El modelo central que representa cada documento de correspondencia. Gestiona el estado, los adjuntos, y las relaciones entre documentos (respuestas).
*   `hr.department` (extendido): Se añade lógica para gestionar prefijos de correlativos, historial de directores y la capacidad de recibir correspondencia.
*   `correspondence_type`: Permite catalogar los documentos (Ej: Memorando, Circular, Oficio) y asociarles una acción de reporte específica.
*   `hr.department.director.history`: Almacena el historial de directores por departamento, evitando solapamientos de fechas.
*   `correspondence.document.read.status`: Registra qué departamento ha leído un documento, quién y cuándo, proporcionando un acuse de recibo.

### Flujo de Trabajo del Documento

El módulo gestiona tres flujos principales, cada uno con sus propios estados y transiciones:

1.  **Flujo Interno (Departamento a Departamento):**
    *   `Borrador` → `Firmado` → `Enviado` → `Respondido`
    *   Un usuario crea un documento, el director de su departamento lo firma, y se envía a otros departamentos internos.

2.  **Flujo Entrante (Externo a Interno):**
    *   `Recibido` → `Asignado` → `Respondido`
    *   Se registra un documento proveniente de una entidad externa. El equipo de "Gestión Externa" lo asigna a los departamentos internos correspondientes para su gestión.

3.  **Flujo Saliente (Interno a Externo):**
    *   `Borrador` → `Firmado` → `Despachado`
    *   Un departamento interno crea un documento para una entidad externa. Después de ser firmado por el director, el equipo de "Gestión Externa" lo marca como despachado.

Un documento en estado `Enviado` o `Asignado` puede ser marcado como **Leído** por los departamentos destinatarios y se puede **Responder**, lo que crea un nuevo documento enlazado y actualiza el estado del original a `Respondido`.

### Menús y Vistas

*   **Bandeja de Entrada:** Muestra la correspondencia recibida pendiente de acción.
*   **Bandeja de Salida:** Muestra la correspondencia enviada por el usuario actual.
*   **Gestión Externa:** Un menú dedicado para el personal autorizado (ej. Despacho) para gestionar toda la correspondencia entrante y saliente con entidades externas.
*   **Archivo:** Un repositorio completo de toda la correspondencia, con potentes filtros de búsqueda.
*   **Configuración:**
    *   **Departamentos:** Para crear y gestionar los departamentos de la organización.
    *   **Tipos de Correspondencia:** Para definir las categorías de documentos y sus reportes asociados.

## Instalación

### Dependencias:
# Instala dependencias del sistema y librerías de Python necesarias.

RUN apt-get update && apt-get install -y --no-install-recommends wkhtmltopdf && \
    && pip install qrcode \
    apt-get clean && \
    && rm -rf /var/lib/apt/lists/*

1.  Clona o descarga este repositorio.
2.  Añade la carpeta `correspondence` a tu directorio de `addons` de Odoo.
3.  Reinicia el servicio de Odoo.
4.  Activa el modo desarrollador en Odoo.
5.  Ve a `Aplicaciones`, busca "Correspondencia Institucional" e instálalo.

## Diagrama de Flujos

<img width="1024" alt="Diagrama de Flujo de Correspondencia" src="https://github.com/user-attachments/assets/f7cec1d8-ccfe-4a1a-ad0e-9b6a49e90c7a" />
