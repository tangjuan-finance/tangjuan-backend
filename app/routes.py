from app import app
from flask import request
from app.lib import verify_signature
import git
import os
import json

W_SECRET = app.config['W_SECRET']

@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        signature_header = request.headers.get('X-Hub-Signature-256')
        # webhook content type should be application/json for request.data to have the payload
        # request.data is empty in case of x-www-form-urlencoded
        payload_body = request.data
        verify_signature(payload_body, W_SECRET, signature_header)

        payload = request.get_json()
        if payload is None:
            print('Deploy payload is empty: {payload}'.format(
                payload=payload))
            # abort(abort_code)
            return '', 404

        if payload['ref'] != 'refs/heads/main':
            return json.dumps({'msg': 'Not main; ignoring'})
        repo = git.Repo('./f4lazylifes')
        origin = repo.remotes.origin

        pull_info = origin.pull()

        if len(pull_info) == 0:
            return json.dumps({'msg': "Didn't pull any information from remote!"})
        if pull_info[0].flags > 128:
            return json.dumps({'msg': "Didn't pull any information from remote!"})

        commit_hash = pull_info[0].commit.hexsha
        build_commit = f'build_commit = "{commit_hash}"'
        print(f'{build_commit}')
        return 'Updated PythonAnywhere server to commit {commit}'.format(commit=commit_hash), 200
    else:
        return 'Wrong event type', 400

@app.route('/')
@app.route('/index')
def index():
    return "🥳😅 Not sure Hello, World!"