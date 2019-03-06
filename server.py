#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, send_from_directory, redirect, url_for, jsonify, Response
from flask.views import MethodView
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()

    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity,dict())

    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}'

myWorld = World()

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(next(request.form.keys()))

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

@app.route("/")
def index():
    return redirect((url_for("serve_static", filename="index.html")))


class EntityView(MethodView):
    def get(self, entity):
        data = myWorld.get(entity)
        if not data:
            response = Response()
            response.status_code = 404
            return response

        return jsonify(data)

    def post(self, entity):
        return self.put(entity)

    def put(self, entity):
        if entity not in myWorld.world():
            code = 201
        else:
            code = 200

        myWorld.set(entity, flask_post_json())

        response = Response()
        response.status_code = code

        return response

app.add_url_rule("/entity/<entity>", methods=['POST','PUT', 'GET'], view_func=EntityView.as_view("EntityView"))

class WorldView(MethodView):
    def get(self):
        return jsonify(myWorld.world())

    def post(self):
        print(flask_post_json())
        return jsonify(myWorld.world())

app.add_url_rule("/world", methods=("POST", "GET"), view_func=WorldView.as_view("WorldView"))


@app.route("/clear", methods=['POST'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    return jsonify(myWorld.world())



if __name__ == "__main__":
    app.run()
