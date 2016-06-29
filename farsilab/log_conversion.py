" Updated to new TTM 4.7"


from numpy import *

def rebin(t_in, t_out, h_in):
    h_out = zeros(len(t_out))
    h_out[where([t in t_in for t in t_out ])] =  \
        h_in[where([t in t_out for t in t_in])]
    return h_out

def convert_log(filename, average = True,
                       time_bins = False,
                       uniform_binning = True,
                       error_bar = False,
                       count_rate = True,
                       chunks = (0,1e9),
                       limits = (-250000, 250000)):
    f = open(filename)
    hists = []
    s_log = []
    data = {}
    dt = 0
    start_m = None
    stop_m = None
    
    log_read = 0
    while f.read(1):
        l = f.readline()
        ## End of log marker
        if '- - -' in l:
            break

        ## First Line of entry 
        ## Date/time
        l = l.split()
        date,hour = l[1].split('-'), l[2].split(':')
        log_time = int(date[2])*60*60*24 + int(hour[2]) + 60 * int(hour[1]) + 60*60 * int(hour[0])
        if log_read == 1:
            start_m = log_time
        if log_read == 2:
            stop_m = log_time

        ## Second line - Table title " Recent Freq. Table [*2 Ticks @ 82.3045ps] " (skip)
        f.readline()
        
        if not average:
            data = {}
        
        ## Start the histograms line
        line = f.readline()
        ## Extract the data
        while line[0] is ' ':            
            l = line.split(':')
            t,counts = int(l[0]), float(l[-1])
            
            if dt == 0:
                dt = 1
                if len(l) == 3:
                    dt = int(l[1])-int(l[0])+1
                
            if t in data:
                data[t] += counts
            elif (t > limits[0]) and (t < limits[1]):
                data[t] = counts
            line = f.readline()
        log_read += 1
        
        ## Line is "Recent Single Start/Stop Event Counts: Start 1067501 - Stop 643576"

        ## Make sure last line of the entry is a sequence of dashes
        
        while line[0:3] != '---':
            line = f.readline()
            #print ('Unexpected end of log entry')


        ## Skip first log
        if log_read == 1:
            data = {}
        
        ## read only in the chunks
        if log_read < chunks[0]:
            data = {}
            continue
        elif log_read >= chunks[1]:
            data = {}
            break
        
        ## Skip log entries that are empty
        if len(data) == 0:
            continue
            
        ## Convert 'dict' into an array and add to the total
        data_a = array([d for d in data.items()]).T
        data_a[1] = 1.*data_a[1]  # count/sec
        h = data_a[1,argsort(data_a[0])]
        t = sort(data_a[0])
        e = sqrt(h)/h  # relative error
        s_log.append(log_time)
        hists.append([t,h,e])
        
    if count_rate:
        for i in range(len(hists)):
            hists[i][1] =  hists[i][1] / (stop_m-start_m)
    
    ## If average consider only last line
    if average:
        hists = [[hists[-1][0], hists[-1][1], hists[-1][2]]]
        if count_rate:
            
            hists[0][1] = hists[0][1]/(log_read-1-chunks[0])
        time = hists[0][0]
        hists_rebinned = 1.*hists[0][1]
        errors = hists[0][2]
        
            
    
    ## Rebin all on a same scale    
    ## Convert all histogram to same timescale 
    ## i.e. extend the time axis to the largest of the histograms
    limits = amin([amin(h[0]) for h in hists]), amax([amax(h[0]) for h in hists])
    
    if uniform_binning:
        time = arange(limits[0], limits[1] + dt, dt)        
        hists_rebinned = array([rebin(t,time,h) for t,h,e in hists])
        errors = array([rebin(t,time,e) for t,h,e in hists])

        if average:
            hists_rebinned= hists_rebinned[0]
            errors = errors[0]
            
    elif not average :
        time =  [h[0] for h in hists]
        hists_rebinned  =  [h[1] for h in hists]
        errors = [h[2] for h in hists]
        
    if not time_bins:
        if uniform_binning:
            time = time * .0823045
        else:
            time =  [t* .0823045 for t in time]
    
    
    time = array(time)
    errors = array(errors)
    hists_rebinned = array(hists_rebinned)
    
    ## If we are interested in the time evolution, returns the time each
    ## log was taken as well
    if not average:
        hists_rebinned = [array(s_log), array(hists_rebinned)]
    
    
    
    if not count_rate:
        return time, hists_rebinned, (log_read-1)*(stop_m-start_m)
    elif error_bar:
        return time, hists_rebinned, errors*hists_rebinned
    else:
        return time, hists_rebinned