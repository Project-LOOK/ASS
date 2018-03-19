from collections import MutableMapping

class Sensor_db(MutableMapping, dict):
    def __init__(self):
        self._observers = []

    def __getitem__(self,key):
        return dict.__getitem__(self,key)

    def __setitem__(self, key, value):
        dict.__setitem__(self,key,value)
        for callback in self._observers:
            callback(key, value)

    def __delitem__(self, key):
        dict.__delitem__(self,key)
        for callback in self._observers:
            callback(key)
    
    def __iter__(self):
        return dict.__iter__(self)
    
    def __len__(self):
        return dict.__len__(self)
    
    def __contains__(self, x):
        return dict.__contains__(self,x)

    def bind_to(self, cb):
        self._observers.append(cb)

    def __str__(self):
        for value, key in dict.items(self):
            print_str = print_str + str(value) +": " + str(key) + ", "
        print_str = "{" + print_str + "}"
        return print_str

class Sensor(object):
    def __init__(self, address=None):
        self.address = address
        self.svc_path = None
        self.chrc_path = None
        self.path = None

        self._connected = False
        self._value = 0
        self._observers = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.call_cb("value", value)

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, value):
        self._connected = value
        self.call_cb("connected", value)

    def bind_to(self, key, cb):
        self._observers.append({"var": key, "callback": cb})

    def call_cb(self, key, value):
        for observer in self._observers:
            if key == observer['var']:
                observer["callback"](key, value)

    def __str__(self):
        return str(self.address)

if __name__ == '__main__':
    def test_cb(key, value=None):
        print("cb... " + str(key) + ": " + str(value))

    a = Sensor_db()
    a.bind_to(test_cb)

    mysensor = Sensor(address="cc:ee:ff:aa:11:dd")
    a['Mun'] = Sensor(address="28:af:56:aD:17:bc")
    a['derrick'] = mysensor

    a['derrick'].bind_to('value', test_cb)
    a['derrick'].bind_to('connected', test_cb)

    a['derrick'].connected = 50
    a['derrick'].value = 500
    del a['derrick']

    a = True
    print("Type: " + str(type(a)))
