from click import command, option

from platform import system

if system() in ('Darwin', 'Linux'):
    from app import app
else:
    from falcon_reporting.app import app


@command()
@option('--host', '-h', default='0.0.0.0', help='host ip')
@option('--port', '-p', default=5000, help='listening port')
def run(host, port):
    app.run(host=host, port=port)

if __name__ == '__main__':
    run()
