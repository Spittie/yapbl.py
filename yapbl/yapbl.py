import json
import mimetypes
import os
import requests


class PushBullet(object):
    DEVICES_URL = 'https://api.pushbullet.com/v2/devices'

    def __init__(self, api_key):
        self.api_key = api_key
        self._s = requests.session()
        self._s.auth = (self.api_key, '')

    def __repr__(self):
        return '<PushBullet [{}]>'.format(self.api_key)

    def devices(self):
        r = self._s.get(self.DEVICES_URL)
        if r.status_code == 401:
            return 'Authentication error'
        return [Device(self.api_key, device) for device in r.json()['devices']]


class Device(object):
    DEVICES_URL = 'https://api.pushbullet.com/v2/devices'
    PUSH_URL = 'https://api.pushbullet.com/v2/pushes'
    UPLOAD_URL = 'https://api.pushbullet.com/v2/upload-request'
    UPLOAD_LIMIT = 25000000

    def __init__(self, api_key, device):
        self.api_key = api_key
        self.iden = device['iden']
        self.type = device['type']
        self.active = device['active']
        self.model = device['model']
        self.pushable = device['pushable']
        self._s = requests.session()
        self._s.auth = (self.api_key, '')
        self._s.headers = {'Content-Type': 'application/json'}

    def __repr__(self):
        return '<Device [{} - {}]>'.format(self.model, self.iden)

    def _push(self, data):
        data['device_iden'] = self.iden
        return self._s.post(self.PUSH_URL, data=json.dumps(data))

    def push_note(self, title, body):
        data = {'type': 'note',
                'title': title,
                'body': body}
        return self._push(data)

    def push_link(self, url, body=None, title=None):
        data = {'type': 'link',
                'title': title,
                'url': url,
                'body': body}
        return self._push(data)

    def push_address(self, address):
        data = {'type': 'address',
                'address': address}
        return self._push(data)

    def push_list(self, title, items):
        data = {'type': 'list',
                'title': title,
                'items': items}
        return self._push(data)

    def push_file(self, pfile, file_type=None, file_name=None):
        # FP
        if not isinstance(pfile, str):
            if os.fstat(pfile.fileno()).st_size > self.UPLOAD_LIMIT:
                return 'File too big'
            if not file_type:
                file_type = mimetypes.guess_type(pfile.name)
            if not file_name:
                file_name = pfile.name
            payload = {'file_type': file_type,
                       'file_name': file_name}
            r = self._s.get(self.UPLOAD_URL, params=payload)
            file_url = r.json()['file_url']
            upload_url = r.json()['upload_url']
            data = r.json()['data']
            files = {'file': pfile}
            requests.post(upload_url, files=files, data=data)
        # String/url
        else:
            if not file_type:
                file_type = mimetypes.guess_type(pfile)
            if not file_name:
                __, file_name = pfile.rsplit('/', 1)
            file_url = pfile
        data = {'type': 'file',
                'file_type': file_type,
                'file_name': file_name,
                'file_url': file_url}
        return self._push(data)

    def delete(self):
        self._s.delete('{}/{}'.format(self.DEVICES_URL, self.iden))
