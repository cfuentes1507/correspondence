# -*- coding: utf-8 -*-

# Modelos base heredados
from . import hr_employee
from . import hr_department

# Modelos de catálogo
from . import correspondence_type

# Modelos de relación y auxiliares
from . import correspondence_department_director
from . import correspondence_department_correlative

# Modelo principal
from . import correspondence_document

# Modelos secundarios que dependen del principal
from . import correspondence_document_read_status
