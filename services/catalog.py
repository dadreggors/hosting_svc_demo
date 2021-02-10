from flask import Flask, jsonify, make_response
import requests
import os
import simplejson as json
import subprocess

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

database_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#print(database_path)

with open("{}/database/catalog.json".format(database_path), "r") as f:
    usr = json.load(f)

@app.route("/", methods=['GET'])
def index():
    ''' Ask item to look elsewhere '''
    return "Noting useful to see here"

@app.route('/catalog', methods=['GET'])
def catalog():
    ''' Returns the list of catalog items '''

    resp = make_response(json.dumps(usr, sort_keys=True, indent=4))
    resp.headers['Content-Type']="application/json"
    return resp

@app.route('/catalog/<item>', methods=['GET'])
def item_data(item):
    ''' Returns info about a specific item '''

    if item not in usr:
        return "Not found"

    return jsonify(usr[item])

@app.route('/catalog/<item>/features', methods=['GET'])
def features(item):
    ''' Get item features '''

    try:
        req = requests.get("http://127.0.0.1:8090/features/{}".format(item))
    except requests.exceptions.ConnectionError:
        return "Service unavailable"
    return req.text

# Lets add a nice way to catalog service pids and kill them
@app.route('/svcpslist', methods=['GET'])
def ps_list():
    ''' Returns a list of processes '''

    pslist = {}
    proc = subprocess.Popen(['pgrep', '-a', 'python'],stdout=subprocess.PIPE)
    while True:
      line = proc.stdout.readline()
      if not line:
        break
      pid, _, name = line.split()
      pslist[pid] = { "pid": pid, "name": name }
    return jsonify(pslist)

@app.route('/stopsvc', methods=['GET'])
def stopsvc():
    ''' Stops all svc processes '''

    procs = json.loads(ps_list().get_data())
    print("Killing the following processes:")
    for proc in procs:
        print("'{} - {}' ".format(proc, procs[proc]["name"]))
    output = subprocess.check_output(['pkill', 'python'])
    # We will never get here
    return jsonify('{"Status": "Stopped"}')

if __name__ == '__main__':
    app.run(port=8088, debug=True)
