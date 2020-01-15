import os
from flask import Flask, render_template
from bokeh.embed import server_document


def create_app(test_config=None):
    # app factory
    app = Flask(__name__, instance_relative_config=None)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .bkapp.bkapp import BokehApp

    # test file and names, later on it will be provided by the user
    bk_file_path_db = os.path.join(app.root_path, 'gnucash', 'gnucash_files', 'finanse_sql.gnucash')
    bk_names = ['Maciek', 'Justyna']

    bk_port = 9090
    bkapp_server_address = 'http://127.0.0.1:9090/'
    bkapp = BokehApp(bk_file_path_db, bk_port, bk_names)

    from threading import Thread
    Thread(target=bkapp.bkworker).start()

    from .monthly import create_bp

    bp_monthly = create_bp(bkapp_server_address)
    app.register_blueprint(bp_monthly)

    @app.route('/')
    def index():
        script = server_document('http://127.0.0.1:9090/provide')
        return render_template('index.html', script=script)

    return app
