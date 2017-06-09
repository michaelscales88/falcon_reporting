import os
from click import command, option


from app import app


@command()
@option('--host', '-h', default='0.0.0.0', help='host ip')
@option('--port', '-p', default=5000, help='listening port')
def run(host, port):
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))

if __name__ == '__main__':
    run()
