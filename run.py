from click import command, option

from app import app


@command()
@option('--port', '-p', default=5000, help='listening port')
def run(port):
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run()
