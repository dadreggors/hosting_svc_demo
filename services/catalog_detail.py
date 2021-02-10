from flask import Flask, jsonify, make_response
import simplejson as json
import os
import subprocess

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

database_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

with open("{}/database/catalog_detail.json".format(database_path), "r") as jsf:
    feature_list = json.load(jsf)

@app.route('/', methods=['GET'])
def index():
    ''' Ask item to look elsewhere '''
    return "Noting useful to see here"

@app.route('/features', methods=['GET'])
def show_features():
    ''' Displays all the features '''

    tlists = []
    for item in feature_list:
        for lname in feature_list[item]:
            tlists.append(lname)
    return jsonify(features=tlists)

@app.route('/features/<item>', methods=['GET'])
def user_list(item):
    ''' Returns an item oriented list '''

    if item not in feature_list:
        return "No list found"

    return jsonify(feature_list[item])

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
    app.run(port=8090, debug=True)
