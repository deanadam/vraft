from gevent import monkey
monkey.patch_all()
import os
from flask import Flask, jsonify, request
from raft.cluster import Cluster
from timer_thread import TimerThread

NODE_ID = int(os.environ.get('NODE_ID'))
cluster = Cluster()
node = cluster[NODE_ID]
timer_thread = TimerThread(NODE_ID)


def create_app():
    raft = Flask(__name__)
    timer_thread.start()
    return raft


app = create_app()


@app.route('/raft/vote', methods=['POST'])
def request_vote():
    candidate = request.get_json()
    result = timer_thread.vote(candidate)
    return jsonify(result)


@app.route('/raft/heartbeat', methods=['POST'])
def heartbeat():
    leader = request.get_json()
    print(f'follower ({node}) got heartbeat from leader: {leader}')
    d = {"alive": True, "node": node}
    timer_thread.become_follower()
    return jsonify(d)


@app.route('/')
def hello_raft():
    return f'raft cluster: {cluster}!'


if __name__ == '__main__':
    create_app()
    app.run()
