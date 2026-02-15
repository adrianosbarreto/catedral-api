from flask import Blueprint

api = Blueprint('api', __name__)

from . import membros, eventos, celulas, ides, nucleos, frequencias, solicitacoes
