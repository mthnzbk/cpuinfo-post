#!/usr/bin/env python
#-*- coding: utf-8

import sys, time, urllib2, urllib, threading

class GetCpuLoad(object):
    def __init__(self, percentage=True, sleeptime = 1):
        '''
        @parent class: GetCpuLoad
        @date: 04.12.2014
        @author: plagtag
        @info:
        @param:
        @return: CPU load in percentage
        '''
        self.percentage = percentage
        self.cpustat = '/proc/stat'
        self.sep = ' '
        self.sleeptime = sleeptime

    def getcputime(self):
        '''
        http://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux
        read in cpu information from file
        The meanings of the columns are as follows, from left to right:
            0cpuid: number of cpu
            1user: normal processes executing in user mode
            2nice: niced processes executing in user mode
            3system: processes executing in kernel mode
            4idle: twiddling thumbs
            5iowait: waiting for I/O to complete
            6irq: servicing interrupts
            7softirq: servicing softirqs

        #the formulas from htop
             user    nice   system  idle      iowait irq   softirq  steal  guest  guest_nice
        cpu  74608   2520   24433   1117073   6176   4054  0        0      0      0


        Idle=idle+iowait
        NonIdle=user+nice+system+irq+softirq+steal
        Total=Idle+NonIdle # first line of file for all cpus

        CPU_Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)
        '''
        cpu_infos = {} #collect here the information
        with open(self.cpustat,'r') as f_stat:
            lines = [line.split(self.sep) for content in f_stat.readlines() for line in content.split('\n') if line.startswith('cpu')]

            #compute for every cpu
            for cpu_line in lines:
                if '' in cpu_line: cpu_line.remove('')#remove empty elements
                cpu_line = [cpu_line[0]]+[float(i) for i in cpu_line[1:]]#type casting
                #cpu_id,user,nice,system,idle,iowait,irq,softrig,steal,guest,guest_nice = cpu_line

                #Idle=idle+iowait
                #NonIdle=user+nice+system+irq+softrig+steal

                #Total=Idle+NonIdle
                Total = 0
                for i in cpu_line:
                    #print i
                    if type(i) != str:
                        Total += int(i)
                #update dictionionary
                cpu_infos.update({cpu_line[0]: {'total': Total, 'idle': cpu_line[4]+cpu_line[5]}})
                #cpu_infos.update({cpu_id:{'total':Total,'idle':Idle}})
            return cpu_infos

    def getcpuload(self):
        '''
        CPU_Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)

        '''
        start = self.getcputime()
        #wait a second
        time.sleep(self.sleeptime)
        stop = self.getcputime()

        cpu_load = {}

        for cpu in start:
            Total = stop[cpu]['total']
            PrevTotal = start[cpu]['total']

            Idle = stop[cpu]['idle']
            PrevIdle = start[cpu]['idle']
            yuzde = str(((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)*100).split(".")
            CPU_Percentage= "%" + yuzde[0]+"."+yuzde[1][0:2]
            cpu_load.update({cpu: CPU_Percentage})
        return cpu_load


class CpuTimer(threading.Thread):
    data = {}

    def run(self):
        x = GetCpuLoad()
        while True:
            self.data = x.getcpuload()
            #print data


try:
    t = CpuTimer()
    t.start()
    t.join(1)
    tparam, tsecond, uparam, url = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    if tparam != "-t" or uparam != "-url":
        raise Exception

except:
    print ("Yanlış parametre girişi yaptınız!")
    print ("Kullanım: cpuinfo-post.py -t 20 -url http://deneme.com")
    sys.exit()

try:
    while True:
        # işlemci bilgisi post ediliyor.
        request = urllib2.Request(url, urllib.urlencode(t.data))
        post = urllib2.urlopen(request)

        if int(post.code) == 200:
            print (t.data)
            print ("İşlemci bilgisi gönderildi!")
        else:
            print ("Bilgi gönderilemedi!..")

        # parametre olarak girilen saniye kadar bekle.
        time.sleep(tsecond)

# Ctrl+C ile kesme yapılınca düzgün bir çıktı alınıyor.
except KeyboardInterrupt:
    print ("Programdan çıkılıyor...")
    sys.exit()

# Bağlantı hatası alırsak...
except (urllib2.HTTPError, urllib2.URLError):
    print ("Girilen Url'ye bağlanılamıyor...")
