# Single Color RGB565 Blob Tracking Example
#
# This example shows off single color RGB565 tracking using the OpenMV Cam.

import sensor, image, time, math,struct
from pyb import UART
from pyb import LED
threshold_index = 4 # 0 for red, 1 for green, 2 for blue

# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# The below thresholds track in general red/green/blue things. You may wish to tune them...

thresholds = [(50, 100, -8, 26, -4, 18)]

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((500, 440))
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_auto_exposure(False,1200)
clock = time.clock()
a=0
led1=LED(1)
led2=LED(2)
uart = UART(3,115200)  #串口3，波特率115200
# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. "merge=True" merges all overlapping blobs in the image.
def send_data_packet(x, y):
    temp = struct.pack(">bHHb",                #格式为俩个字符俩个整型
                   0xAA,                       #帧头1
                   int(x), # up sample by 4    #数据1
                   int(y), # up sample by 4    #数据2
                   0xAE)                       #帧头2
    uart.write(temp)


#def receive_date_pack(x):
    #temp=struct.pack(">bHHb",
                     #0xAA,
                     #int(x),
                     #0xAE)

#找到最大色块
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob


while(True):
    clock.tick()
    img = sensor.snapshot()
    if a==0:
        blobs=img.find_blobs([thresholds[0]],roi=(50,50,100,100), pixels_threshold=60, area_threshold=60, merge=True)
        if blobs==0:
            led2.off()#灭
            send_data_packet(888,888)
        if blobs:
            max_blob=find_max(blobs)
            # These values depend on the blob not being circular - otherwise they will be shaky.
            # These values are stable all the time.
            led2.on()#亮
            img.draw_rectangle(max_blob.rect())
            img.draw_cross(max_blob.cx(), max_blob.cy())
            send_data_packet(max_blob.cx(), max_blob.cy())
            print(max_blob.cx(), max_blob.cy())
            # Note - the blob rotation is unique to 0-180 only.
            img.draw_keypoints([(max_blob.cx(), max_blob.cy(), int(math.degrees(max_blob.rotation())))], size=20)
    print(clock.fps())
