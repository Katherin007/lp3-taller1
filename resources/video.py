"""
Recursos y rutas para la API de videos
"""
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from models.video import VideoModel
from models import db
import logging
from prometheus_cliente import generate_latest, CONTENT_TYPE_LATESST, Counter, Histogram
from flask import make_response

# configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
request_counter = Counter('http_request_total', 'Total number of HTTP requests', ['method', 'endpoint'])
response_histogram = Histogram('http_response_time_seconds', 'HTTP responses time in seconds', ['method', 'endpoint'])

# Campos para serializar respuestas
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'views': fields.Integer,
    'likes': fields.Integer
}

# Parser para los argumentos en solicitudes PUT (crear video)
video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Nombre del video es requerido", required=True)
video_put_args.add_argument("views", type=int, help="Número de vistas del video", required=True)
video_put_args.add_argument("likes", type=int, help="Número de likes del video", required=True)

# Parser para los argumentos en solicitudes PATCH (actualizar video)
video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="Nombre del video")
video_update_args.add_argument("views", type=int, help="Número de vistas del video")
video_update_args.add_argument("likes", type=int, help="Número de likes del video")

def abort_if_video_doesnt_exist(video_id):
    """
    Verifica si un video existe, y si no, aborta la solicitud
    
    Args:
        video_id (int): ID del video a verificar
    """
    video = VideoModel.query.filter_by(id=video_id).first()
    if not video:
        abort(404, message=f"No se encontró un video con el ID {video_id}")
    return video

class Video(Resource):
    """
    Recurso para gestionar videos individuales
    
    Métodos:
        get: Obtener un video por ID
        put: Crear un nuevo video
        patch: Actualizar un video existente
        delete: Eliminar un video
    """
    
    @marshal_with(resource_fields)
    def get(self, video_id):
        """
        Obtiene un video por su ID
        
        Args:
            video_id (int): ID del video a obtener
            
        Returns:
            VideoModel: El video solicitado
        """
        video = abort_if_video_doesnt_exist(video_id)
        return video, 200
        # TODO
    
    
    @marshal_with(resource_fields)
    def put(self, video_id):
        """
        Crea un nuevo video con un ID específico
        
        Args:
            video_id (int): ID para el nuevo video
            
        Returns:
            VideoModel: El video creado
        """
        
        request_counter.labels(method='PUT', endpoint='/video/<int:video_id>').inc()
        with response_histogram.labels(method='PUT', endpoint='/video/<int:video_id}').time():
            args = video_put_args.parse_args()
            logging.info(f"Creando video con ID {video_id} y nombre {args['name']}")    
            
        # Verifica si el video ya existe
            existing_video = VideoModel.query.get(video_id)
            if existing_video:
                logging.warning(f"El video con ID {video_id} ya existe")
                abort(409, message=f"Ya existe un video con el ID {video_id}")
            video = VideoModel(id=video_id, name=args["name"], views=args["views"], likes=args["likes"])
            db.session.add(video)
            db.session.commit()
            return video, 201
            # TODO
        
    
    @marshal_with(resource_fields)
    def patch(self, video_id):
        """
        Actualiza un video existente
        
        Args:
            video_id (int): ID del video a actualizar
            
        Returns:
            VideoModel: El video actualizado
        """
        request_counter.labels(method='PATCH', endpoint='/video/<int:video_id>').inc()
        with response_histogram.labels(method='PATCH', endpoint='/video/<int:video_id}').time():
            logging.info(f"Actualizando video con ID {video_id}")
            video = abort_if_video_doesnt_exist(video_id)
            args = video_update_args.parse_args()
 
            if args["name"] is not None:
                logging.info(f"Actualizando nombre del video a {args['name']}") 
                video.name = args["name"]
            if args["views"] is not None:
                logging.info(f"Actualizando vistas del video a {args['views']}")    
                video.views = args["views"]
            if args["likes"] is not None:
                logging.info(f"Actualizando likes del video a {args['likes']}")
                video.likes = args["likes"]
            db.session.commit()
            return video, 200 
        # TODO
        
    
    def delete(self, video_id):
        """
        Elimina un video existente
        
        Args:
            video_id (int): ID del video a eliminar
            
        Returns:
            str: Mensaje vacío con código 204
        """
        request_counter.labels(method='DELETE', endpoint='/video/<int:video_id>').inc()
        with response_histogram.labels(method='DELETE', endpoint='/video/<int:video_id}').time():
            logging.info(f"Eliminando video con ID {video_id}")
            video = abort_if_video_doesnt_exist(video_id)
            db.session.delete(video)
            db.session.commit()
            logging.info(f"Video con ID {video_id} eliminado")
            return {'message': f'Video con id {video_id} eliminado'}, 204
    # TODO
    class Metrics(Resource):
        """
        Recurso para obtener métricas de la API
        """
        def get(self):
            """
            Obtiene las métricas de la API
            
            Returns:
                Response: Respuesta con las métricas en formato Prometheus
            """
            request_counter.labels(method='GET', endpoint='/metrics').inc()
            with response_histogram.labels(method='GET', endpoint='/metrics').time():    
                      return make_response(generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATESST})
    
        

