"""
This file runs the server of our flask app.
You can specify a port number and run with the below command:

python3 runserver.py <portnumber>
"""
import argparse
from sys import argv, exit, stderr
from mtbapp import app

def main():
    """
    Main function for the flask app,
    where we check for command line input and start the server.
    """
    port = get_host_port()
    try:
        app.run(host='0.0.0.0', port=port, debug=True, threaded=True, ssl_context=('cert.pem', 'key.pem'))
    except ConnectionRefusedError as ex:
        print(ex, file=stderr)
        exit(1)

def get_host_port():
    """Parse the input to get the host port number
    """
    if len(argv) > 2:
        print('Usage: python reg.py [-h] port', file=stderr)
        exit(1)

    parser = argparse.ArgumentParser(allow_abbrev=False,
                    description="The registrar application")
    parser.add_argument('port', metavar='port', type=int, nargs=1,
                    help='the port at which the server should listen')
    args = parser.parse_args()

    port = None
    if args.port:
        port = args.port[0]
    return port

if __name__ == '__main__':
    main()
