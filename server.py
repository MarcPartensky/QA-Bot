#!/usr/bin/env python
"""
Restful api for using the transformers library in pypi.
This library could be used to do remote questions answering,
text summarization and will be used in my own website and discord bot.
"""
from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse

from transformers import pipeline

import html2text
import requests
import time

ask = pipeline("question-answering")
summarize = pipeline("summarization")

h = html2text.HTML2Text()
ignore_links = True

app = Flask(__name__)
api = Api(app)

context_parser = reqparse.RequestParser()

class HelloWorld(Resource):
    """Implement flask restful resource for testing."""

    def get(self):
        """Return hello world"""
        return {'hello': 'world'}

contexts = {}

# class QuestionAnswering(Resource):
#     """Answer your questions given a context."""

#     def post(self, id=None):
#         """Post a context."""
#         if not id
#         id = len(contexts)
#         contexts[id] = parser.parse_args()
#         return id

#     def put(self, id):
#         """Change a context."""
#         contexts[id] = parser.parse_args()

#     def delete(self, id):
#         """Delete a context."""
#         del contexts[id]

#     def get(self, id, question:str):
#         """Answer a question about the context."""
#         return npl(question=question, context=contexts[id])

# class QuestionAnswering()

class Context(Resource):
    """Store of contexts."""
    def post(self, id=None):
        """Post a context."""
        if not id:
            id = len(contexts)
        contexts[id] = context_parser.parse_args()
        return id

    def get(self, id):
        """Return a context."""
        return contexts[id]

test_parser = reqparse.RequestParser()
test_parser.add_argument('context')
test_parser.add_argument('url')
test_parser.add_argument('question')
test_parser.add_argument('questions')

class Ask(Resource):
    """Ask questions on a text."""

    def get(self):
        """Return a form to ask questions."""
        # Not done yet, cause lazy to do front
        return render_template('ask.html')

    def post(self):
        """Ask a question about a context."""
        t = time.time()
        args = test_parser.parse_args()
        print(args)
        d = {}

        if args['context']:
            context = args['context']
        elif args['url']:
            url = args['url']
            html= requests.get(url).text
            context = h.handle(html)
            # d['context'] = context
            print('context', context)
        else:
            raise Exception

        if args['question']:
            question = args['question']
            response = ask(
                question=question,
                context=context
            )
        elif args['questions']:
            response = [
                ask(
                    question=question,
                    context=context
                ) for question in args['questions']
            ]
        else:
            raise Exception

        d['duration'] = time.time() - t
        response.update(d)
        return response
# api.add_resource(QuestionAnswering, '/ask/<string:id>/')
# api.add_resource(Context, '/context/<string:id>')

summarize_parser = reqparse.RequestParser()
summarize_parser.add_argument('context')

class Summarize:
    """Summarize a text."""

    def post(self):
        """Post a text to summarize."""
        response = {}
        args = test_parser.parse_args()
        if args['context']:
            context = args['context']
        elif args['url']:
            context = requests.get(args['url']).text
        else:
            raise Exception("No context given.")
        max_length = args['max_length']
        min_length = args['min_length']
        do_sample = args['do_sample']

        response.update(
            summarize(
                context,
                max_length=max_length,
                min_length=min_length,
                do_sample=do_sample
            )
        )
        return response


api.add_resource(HelloWorld, '/')
api.add_resource(Ask, '/ask')
api.add_ressource(Summarize, '/sum-up')

if __name__ == '__main__':
    app.run(debug=True)
