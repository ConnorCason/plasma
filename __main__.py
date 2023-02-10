import base64, codecs, logging, os, json, requests, sys

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

REST_HOST = os.environ.get('LND_REST_HOST')
MACAROON_PATH = os.environ.get('LND_MACAROON_PATH')
TLS_PATH = os.environ.get('LND_TLS_PATH')

def getinfo():
    log.info('Retreiving node information from /getinfo...')
    url = f'https://{REST_HOST}/v1/getinfo'
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    r = requests.get(url, headers=headers, verify=TLS_PATH)
    return json.dumps(r.json(), indent=2)


if __name__ == "__main__":
    log.info(
    f'''
    Running with the following environment variables:
        $REST_HOST = {REST_HOST}
        $MACAROON_PATH = {MACAROON_PATH}
        $TLS_PATH = {TLS_PATH}
    '''
    )
    print(getinfo())
