"""
Simple Flask backend.
"""
import datetime
import logging
import os

import flask
from flask import Flask, jsonify, request
from flask_pydantic import validate
import json

import database
import settings
import tasks

from models.output import DataOutPut
from models.input import JobInput

flask_app = flask.Flask(__name__)
flask_app.logger.setLevel(logging.INFO)
flask_app.config.update(
    CELERY_RESULT_BACKEND=os.environ.get("CELERY_RESULT_BACKEND"),
    CELERY_BROKER_URL=os.environ["CELERY_BROKER_URL"])

celery_app = tasks.make_celery(flask_app)


def timestamp2iso(t):
    return '' if t is None else datetime.datetime.fromtimestamp(t).isoformat()


@flask_app.route("/lyrics", methods=["POST"])
def get_lyrics():
    inputs = json.loads(request.data)

    def sublist(lst1, lst2):
        return set(lst1) <= set(lst2)

    if sublist(['user', 'playlist_id', 'project_name'], inputs.keys()):
        # if these things are in the post request
        if "threshold" in inputs:
            threshold = inputs['threshold']
        else:
            threshold = 5
        if 'num_threads' in inputs:
            num_threads = inputs['num_threads']
        else:
            num_threads = 3
        if 'debug' in inputs:
            debug = inputs['debug']
        else:
            debug = False

    task_id = tasks.create_s2p_task(user=inputs['user'], playlist_id=inputs['playlist_id'],
                                    project_name=inputs['project_name'], debug=inputs['debug'],
                                    num_threads=inputs['num_threads'], threshold=inputs['threshold'])
    flask_app.logger.info(f"Created new task{task_id}")
    return {"task_id": task_id}


@flask_app.route("/t/<task_id>")
def get_task(task_id):
    all_tasks = [
        {"id": id,
         "created": timestamp2iso(created),
         "finished": timestamp2iso(finished),
         "result": result or ''}
        for id, created, finished, result in database.get_task(task_id)]
    return {"all_tasks": all_tasks}


@flask_app.route("/", methods=["GET"])
def get_index():
    return flask.render_template("index.html")


@flask_app.route("/tasks-json", methods=["GET"])
def get_tasks_json():
    all_tasks = [
        {"id": id,
         "created": timestamp2iso(created),
         "finished": timestamp2iso(finished),
         "result": result or ''}
        for id, created, finished, result in database.get_all()]
    return {"all_tasks": all_tasks}


@flask_app.route("/task", methods=["POST"])
def post_task():
    if not flask.request.is_json:
        flask_app.logger.warning("Invalid non-JSON request with content type '%s'", flask.request.content_type)
        flask.abort(405)
    data = flask.request.json
    str_a, str_b = data["str_a"], data["str_b"]
    task_id = tasks.create_lcs_task(str_a, str_b)
    flask_app.logger.info(
        "Created new task %d for computing LCS of str_a (%d chars) and str_b (%d chars)",
        task_id, len(str_a), len(str_b))
    return {"task_id": task_id}


if __name__ == "__main__":
    if not os.path.exists(settings.database_path):
        database.init()
        flask_app.logger.info("Created database %s", settings.database_path)
    else:
        flask_app.logger.info("Using existing database %s", settings.database_path)
    flask_app.run(host='0.0.0.0', port='5000')
