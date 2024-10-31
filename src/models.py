from dataclasses import dataclass
from datetime import datetime

@dataclass
class Evento:
    id: int
    fecha_hora: datetime
    descripcion: str