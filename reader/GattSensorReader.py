import pygatt

class GattSensorReader():

    def readRawData(self,MAC_ADDRESS,CHARACTERISTIC_UUID):
        if(MAC_ADDRESS == ""):
            raise ValueError('Mac address missing')
        if(CHARACTERISTIC_UUID == ""):
            raise ValueError('Characteristic UUID missing')

        adapter = pygatt.GATTToolBackend()
        adapter.start()
        device = adapter.connect(MAC_ADDRESS, 15)
        value = device.char_read(CHARACTERISTIC_UUID)
        return ''.join('{:02x} '.format(x) for x in value)
