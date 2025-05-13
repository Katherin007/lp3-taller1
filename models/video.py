"""
Modelo de datos para Video
"""
from models import db

class VideoModel(db.Model):
    """
    Modelo para representar un video.
    
    Atributos:
        id (int): Identificador único del video
        name (str): Nombre del video
        views (int): Número de vistas del video
        likes (int): Número de likes del video
    """
    # Nombre de la tabla en la base de datos
    __tablename__ = 'video_model'
    
    # Definición de columnas
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """
        Representación en string del objeto Video
        """
        return f"Video(id={self.id}, name={self.name}, views={self.views}, likes={self.likes})"

