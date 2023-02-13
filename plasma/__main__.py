from lnd_rest.endpoints import *

if __name__ == "__main__":
    print(
    f'''
    Running with the following environment variables:
        $REST_HOST = {REST_HOST}
        $MACAROON_PATH = {MACAROON_PATH}
        $TLS_PATH = {TLS_PATH}
    '''
    )
    get_forwarding_history()
    