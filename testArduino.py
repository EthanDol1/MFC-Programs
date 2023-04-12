import pyfirmata as pf

b = pf.Arduino("COM3")
it = pf.util.Iterator(b)
it.start()

pin = b.get_pin('d:9:p')
