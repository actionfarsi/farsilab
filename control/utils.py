def filename(extension = 'mat'):
    """ Helper for saving files """
    file_list = [ f for f in os.listdir('.') if f[-3:] == extension] # get file list
    file_list.sort(key = os.path.getctime) # order by time
    
    file_name = "scan"
    if len(file_list)!= 0:
        m = re.match('(\D*)(\d*).mat', file_list[-1])
        if m:
            try:
                file_name = m.group(1) + "%d"%(int(m.group(2))+1)
            except:
                file_name = m.group(1) + str(1)
    
    print "Insert filename (if nothing %s.mat) --> "%file_name,
    input_name = raw_input()
    
    ## Overwriting control
    while True:
        if input_name != "":
            file_name = input_name
        
        if file_name+".mat" in file_list:
            print "\nWARNING! File will be overwritten.\nPress Enter to confirm. Otherwise type a new name --> ",
            input_name = raw_input()
            if input_name == "":
                break
            continue
        
        break
    return file_name