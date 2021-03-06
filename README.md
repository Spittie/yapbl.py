# YAPBL.py
## Yet Another PushBullet Library

This is a simple library to utilize PushBullet from Python. It doesn't try to do any magic, but tries to be simple to use.

### Features
* Support Python 2/3 (Tested with Python 2.7.6 and Python 3.4.1)
* Support push to your whole PushBullet account, your devices and your contacts
* Support pushing of local and remote (urls) files
* Read your api key from the os environment
* Use the v2 api
* Single file, easy to drop in a quick project

### Requirements
* Python 2/3
* [requests](python-requests.org)

### How to install
You can just download [yabpl.py](https://raw.githubusercontent.com/Spittie/yapbl.py/master/yapbl/yapbl.py) from the repository, and drop it into your project.  
Now on PyPI! Install with  ```pip install yapbl```

### How to use it
Most methods are supported by every class, so for example you can use  
```.push_note('something', 'something')``` on a device, a contact or your whole pushbullet account

```python

# Import it
from yapbl import PushBullet

# Create a PushBullet instance
# Obviously replace api_key with your actual Api Key
# You can get one from https://www.pushbullet.com/account
# api_key is optional
# If not present yapbl will search PUSHBULLET_API_KEY in os.environ
p = PushBullet(api_key)

# Get your devices
# It will return an array with your active devices
devices = p.devices()

# Get your contacts
# It will return an array with your active contacts
contacts = p.contacts()

# Pass in only_active=False to get every device/contact
every_devices = p.devices(only_active=False)
every_contacts = p.contacts(only_active=False)

# Send a note to every device/contact
p.push_note('title', 'body')

# Send a note to your first device
devices[0].push_note('title', 'body')

# Send a note to your first contact
contacts[0].push_note('title', 'body')

# You can send links
p.push_link('https://www.pushbullet.com', title='PushBullet', body='Testing')

# Title and body are optional
p.push_link('https://www.pushbullet.com')

# You can push an address
p.push_address('Milan, Italy')

# You can push a list
# The items of the list are an array
p.push_list('Test list', ['first', 'second', 'third', 'fourth'])

# You can send a local file
# Max size is 25MB
p.push_file(open('local.png', 'rb'))

# And you can send a remote url
# There's no size limit for that
p.push_file('https://www.pushbullet.com/img/header-logo.png')

# You can add an optional body to that
p.push_file('https://www.pushbullet.com/img/header-logo.png', body='hi!')

# yapbl will try to guess the correct mimetype based on the filename
# But you can always override that
p.push_file('https://www.pushbullet.com/img/header-logo.png', file_type='image/png')

# You can set a custom filename as well
# Otherwise the actual name will be used
p.push_file('https://www.pushbullet.com/img/header-logo.png' file_name='image.png')

# You can create a new stream device
# device_type is optional and default to 'stream'
p.create_device('nickname')

# You can delete a device or a contact
devices[0].delete()
contacts[0].delete()

# Devices have various proprieties
d = devices[0]
d.iden
d.type
d.created
d.modified
d.active
d.pushable

# Contacts too
c = contacts[0]
c.iden
c.email
c.type

# You can access the full reply with the .json propriety
d.json
c.json
```

If there is any problem with the connection, yapbl will raise a TypeError.