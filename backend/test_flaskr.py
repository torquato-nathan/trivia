import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):

	def setUp(self):
		self.app = create_app()
		self.client = self.app.test_client
		self.database_name = "trivia_test"
		self.database_path = f"postgresql://postgres:postgres@localhost:5432/{self.database_name}"
		setup_db(self.app, self.database_path)

		# binds the app to the current context
		with self.app.app_context():
			self.db = SQLAlchemy()
			self.db.init_app(self.app)
			self.db.create_all()
	
	def tearDown(self):
		"""Executed after reach test"""
		pass

	def test_200_get_categories(self):
		res = self.client().get('/categories')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['categories'])
		self.assertTrue(len(data['categories']))

	def test_200_get_category_questions(self):
		category_id = 1
		res = self.client().get(f'/categories/{category_id}/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['questions'])
		self.assertTrue(len(data['questions']))
		self.assertTrue(data['total_questions'])
		self.assertEqual(data['current_category'], category_id)
	
	def test_404_get_category_questions_if_non_existing_category(self):
		category_id = 100
		res = self.client().get(f'/categories/{category_id}/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
	
	def test_200_get_quizz_question(self):
		payload = {
			'previous_questions': [2],
			'category_id': 1
		}

		res = self.client().post('/quizzes', json=payload)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertEqual(data['previous_questions'], payload['previous_questions'])
		self.assertEqual(data['category_id'], payload['category_id'])
		self.assertTrue(data['question'])
		self.assertTrue(data['question']['id'])
		self.assertTrue(data['question']['question'])
		self.assertTrue(data['question']['answer'])
		self.assertTrue(data['question']['category'])
		self.assertTrue(data['question']['difficulty'])
	
	def test_400_get_quizz_question_if_previous_questions_not_provided(self):
		payload = {
			'category_id': 1
		}

		res = self.client().post('/quizzes', json=payload)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 400)
		self.assertEqual(data['success'], False)
	
	def test_200_get_questions(self):
		res = self.client().get('/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['questions'])
		self.assertTrue(len(data['questions']))
		self.assertTrue(data['total_questions'])
		self.assertTrue(data['categories'])
		self.assertTrue(len(data['categories']))
		self.assertEqual(data['current_category'], None)

	def test_404_get_questions_if_non_existing_page(self):
		res = self.client().get('/questions?page=100')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)	

# Make the tests conveniently executable
if __name__ == "__main__":
	unittest.main()