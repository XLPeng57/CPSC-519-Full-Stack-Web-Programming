"""handles user input port number and setup server"""
from sys import stderr, exit, argv
import argparse
from regapp import app


def main():
    """create port and set up server"""
    parser = argparse.ArgumentParser(
        allow_abbrev=False, description='The registrar application')

    parser.add_argument('port',
                        type=int,
                        nargs=1,
                        help='the port at which the server should listen')

    parser.parse_args()

    try:
        port = int(argv[1])
    except Exception:
        print('Port must be an integer.', file=stderr)
        exit(1)

    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
