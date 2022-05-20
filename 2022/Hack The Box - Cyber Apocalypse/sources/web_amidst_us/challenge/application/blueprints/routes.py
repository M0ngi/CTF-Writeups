from flask import Blueprint, request, render_template, abort
from application.util import make_alpha

web = Blueprint('web', __name__)
api = Blueprint('api', __name__)

@web.route('/')
def index():
	return render_template('index.html')

@api.route('/alphafy', methods=['POST'])
def alphafy():
	if not request.is_json or 'image' not in request.json:
		return abort(400)

	return make_alpha(request.json)