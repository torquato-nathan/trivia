import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def serialise_entity_list(entity_list):
  serialised_list = [entity.serialise() for entity in entity_list]
  return serialised_list

def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  def get_categories_map():
    categories = Category.query.all()
    serialised_list = serialise_entity_list(categories)

    return {
      category['id']: category['type'] for category in serialised_list
    }
  
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()
    
    return jsonify({
      'success': True,
      'categories': get_categories_map(),
    })

  @app.route('/categories/<category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    page = request.args.get('page', 1, type=int)
    filter_query = Question.category == category_id
    questions = Question.query.order_by(
      Question.id.asc()
    ).filter(
      filter_query
    ).paginate(
      page, max_per_page=QUESTIONS_PER_PAGE
    )

    return jsonify({
      'success': True,
      'questions': serialise_entity_list(questions.items),
      'total_questions': questions.total,
      'current_category': category_id,
    })

  @app.route('/quizzes', methods=['POST'])
  def get_quizz_question():
    body = request.get_json()
    previous_questions = body['previous_questions']
    category_id = body['category_id']

    if not ('previous_questions' in body):
      abort(422)

    question = Question.query.filter(
      Question.id.notin_((previous_questions)),
      Question.category == category_id if category_id else Question.category > 0
    ).order_by(func.random()).first()

    return jsonify({
      'success': True,
      'question': question.serialise() if question else None,
      'previous_questions': previous_questions,
      'category_id': category_id if category_id else None,
    })

  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    questions = Question.query.order_by(
      Question.id.asc()
    ).paginate(page, max_per_page=QUESTIONS_PER_PAGE)
    
    return jsonify({
      'success': True,
      'questions': serialise_entity_list(questions.items),
      'total_questions': questions.total,
      'categories': get_categories_map(),
      'current_category': None,
    })

  @app.route('/questions', methods=['POST'])
  def create_question():
    try:
      props = request.get_json()
      question = Question(props)
      question.insert()

      return jsonify({
        'success': True,
        'question': question.serialise()
      })
    except:
      abort(422)

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search_term = request.get_json()['searchTerm']
    filter_query = Question.question.ilike("%" + search_term + "%")
    page = request.args.get('page', 1, type=int)
    questions = Question.query.order_by(
      Question.id.asc()
    ).filter(
      filter_query
    ).paginate(
      page, max_per_page=QUESTIONS_PER_PAGE
    )

    return jsonify({
      'success': True,
      'questions': serialise_entity_list(questions.items),
      'total_questions': questions.total,
      'current_category': None,
    })

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.get_or_404(id)
    question.delete()

    return jsonify({
      'success': True,
      'id': question.id
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    