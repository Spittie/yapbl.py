import json
import mimetypes
import os
import requests


def _pushbullet_responses(r):
    if r.status_code == 200:
        return True
    elif r.status_code == 204:
        return True     # File upload
    elif r.status_code == 400:
        raise TypeError('Bad request')
    elif r.status_code == 401:
        raise TypeError('Invalid Api Key')
    elif r.status_code == 403:
        raise TypeError('Invalid Api Key')
    elif r.status_code == 404:
        raise TypeError('Item not found')
    else:
        raise TypeError('Server Error')


class _PushBullet(object):
    DEVICES_URL = 'https://api.pushbullet.com/v2/devices'
    PUSH_URL = 'https://api.pushbullet.com/v2/pushes'
    UPLOAD_URL = 'https://api.pushbullet.com/v2/upload-request'
    UPLOAD_LIMIT = 25*1024*1024
    CONTACTS_URL = 'https://api.pushbullet.com/v2/contacts'

    def __init__(self, api_key=None):
        self.api_key = api_key
        if not api_key:
            try:
                self.api_key = os.getenv('PUSHBULLET_API_KEY')
            except KeyError:
                raise TypeError('Missing api_key')
        self._s = requests.session()
        self._s.auth = (self.api_key, '')
        self._s.headers = {'Content-Type': 'application/json'}

    def _push(self, data):
        if hasattr(locals()['self'], 'iden'):
            data['device_iden'] = self.iden
        if hasattr(locals()['self'], 'email'):
            data['email'] = self.email
        return _pushbullet_responses(self._s.post(self.PUSH_URL, data=json.dumps(data)))

    def push_note(self, title, body):
        data = {'type': 'note',
                'title': title,
                'body': body}
        return self._push(data)

    def push_link(self, url, title=None, body=None):
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

    def push_file(self, pfile, body=None, file_type=None, file_name=None):
        # FP
        if not isinstance(pfile, str):
            if os.fstat(pfile.fileno()).st_size > self.UPLOAD_LIMIT:
                return 'File too big'
            if not file_type:
                file_type, __ = mimetypes.guess_type(pfile.name)
            if not file_name:
                file_name = pfile.name
            payload = {'file_type': file_type,
                       'file_name': file_name}
            r = self._s.get(self.UPLOAD_URL, params=payload)
            _pushbullet_responses(r)
            file_url = r.json()['file_url']
            upload_url = r.json()['upload_url']
            data = r.json()['data']
            files = {'file': pfile}
            _pushbullet_responses(requests.post(upload_url, files=files, data=data))
        # String/url
        else:
            if not file_type:
                file_type, __ = mimetypes.guess_type(pfile)
            if not file_name:
                __, file_name = pfile.rsplit('/', 1)
            file_url = pfile
        data = {'type': 'file',
                'file_type': file_type,
                'file_name': file_name,
                'file_url': file_url,
                'body': body}
        return self._push(data)


class PushBullet(_PushBullet):
    def __repr__(self):
        return '<PushBullet [{}]>'.format(self.api_key)

    def devices(self):
        r = self._s.get(self.DEVICES_URL)
        _pushbullet_responses(r)
        return [Device(device, self.api_key) for device in r.json()['devices'] if device['active'] is not False]

    def contacts(self):
        r = self._s.get(self.CONTACTS_URL)
        _pushbullet_responses(r)
        return [Contact(contact, self.api_key) for contact in r.json()['contacts'] if contact['active'] is not False]


class Device(_PushBullet):
    def __init__(self, device, api_key=None):
        self.iden = device['iden']
        self.model = device['model']
        self.pushable = device['pushable']
        super(Device, self).__init__(api_key)

    def __repr__(self):
        return '<Device [{} - {}]>'.format(self.model, self.iden)

    def delete(self):
        return _pushbullet_responses(self._s.delete('{}/{}'.format(self.DEVICES_URL, self.iden)))


class Contact(_PushBullet):
    def __init__(self, contact, api_key=None):
        self.iden = contact['iden']
        self.email = contact['email']
        self.name = contact['name']
        super(Contact, self).__init__(api_key)

    def __repr__(self):
        return '<Contact [{} - {}]>'.format(self.name, self.email)

    def delete(self):
        return _pushbullet_responses(self._s.delete('{}/{}'.format(self.CONTACTS_URL, self.iden)))