from flask import Blueprint


api=Blueprint('api_1_0',__name__)

from . import main_views 
from . import produce_views