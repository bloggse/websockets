from gevent import monkey
monkey.patch_all()


from flask import Flask, render_template
from flask_socketio import SocketIO
import os

app = Flask(__name__)

if os.path.exists("/etc/bse/bse.conf.py"):
    app.config.from_pyfile("/etc/bse/bse.conf.py")
else:
    app.config.from_object("socmongo.config")

from datamongo import Connection
# give datamongo the database and mc-connection info from config
c = Connection(
    hostURI=app.config["DATABASE_SERVER"],
    memcache_config=app.config["BSE"]["memcache"])

from werkzeug.contrib.cache import MemcachedCache
app.cache = MemcachedCache(c.cache_connection)

socketio = SocketIO(app)

# app.run(host="0.0.0.0",port=5095,debug=True)

@app.route("/")
def ws_test():
    return render_template('websockets.html')


@socketio.on('connect', namespace='/test')
def ws_conn():
    c = app.cache.get('test_counter') or 0
    c += 1
    app.cache.set('test_counter', c)
    print("connect", c)
    socketio.emit('msg', {'count': c}, namespace='/test')

@socketio.on('disconnect', namespace='/test')
def ws_disconn():
    c = app.cache.get('test_counter') or 0
    if c:
        c -= 1
        app.cache.set('test_counter', c)
    print("disconnect", c)
    socketio.emit('msg', {'count': c}, namespace='/test')

@socketio.on('message')
def handle_message(message, namespace='/test'):
    print('received message')
    print(message)


if __name__ == '__main__':
    socketio.run(app)