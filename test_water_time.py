from psychopy import visual, core,monitors,data, event,gui# import some libraries from PsychoPy

import nidaqmx as ni
water_time = 90
water_daq = ni.Task()
water_daq.do_channels.add_do_chan('Dev1/Port1/Line2')
core.wait(.5)
water_daq.start()
for _ in range(5):
       water_daq.write(True)
       core.wait(water_time/1000)
       water_daq.write(False)
       core.wait(4)
water_daq.stop()
water_daq.close()