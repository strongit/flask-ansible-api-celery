#!/usr/bin/python
#coding:utf-8
from celery import Celery
import json
from flask import Flask, abort, jsonify, request, session
from ansible.inventory import Inventory
from ansible.playbook  import PlayBook
from ansible import callbacks
import jinja2
from tempfile import NamedTemporaryFile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def adduser(ips, users):
    inventory ="""
    {% for i in hosts -%}
    {{ i }}
    {% endfor %}
    """
    inventory_template = jinja2.Template(inventory)
    rendered_inventory = inventory_template.render({'hosts': ips})
    hosts = NamedTemporaryFile(delete=False,suffix='tmp',dir='/tmp/ansible/')
    hosts.write(rendered_inventory)
    hosts.close()
    inventory = Inventory(hosts.name)
    stats =  callbacks.AggregateStats()
    playbook_cb =callbacks.PlaybookCallbacks()
    runner_cb   =callbacks.PlaybookRunnerCallbacks(stats)
    vars={}
    vars['users'] = users
    results = PlayBook(playbook='user.yaml',callbacks=playbook_cb,runner_callbacks=runner_cb,stats=stats,inventory=inventory,extra_vars=vars)
    res = results.run()
    logs = []
    logs.append("finish playbook\n")
    logs.append(str(res))
    return  logs

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/add",methods=['POST'])
def one():
    ips = [ i.encode('ascii') for i in request.form.getlist('ips') ]
    users = [ i.encode('ascii') for i in request.form.getlist('users') ]
    res = adduser.apply_async((ips, users))
    context = {"id": res.task_id, "ips": ips, "users": users}
    result = "add((ips){0}, (users){1})".format(context['ips'], context['users'])
    goto = "{0}".format(context['id'])
    return jsonify(result=result, goto=goto)

@app.route("/add/result/<task_id>")
def show_add_result(task_id):
    task = adduser.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': task.info,  
        }
    return jsonify(response)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
