
import time, os, datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from staging import *
import shutil
csv_format = False
curr_time = None
log = None
file_types = "mp4","avi"

to_copy_stack = ""  # Needed to overcome permission error in creating a new file.
                    # Reason: when a file is just created, it cannot be copied readily until it is modified
                    # by the system. This happens automatically but in another event, which is on_modified

try:
    if(csv_format):
        log = open("logs/logs.csv","a+")
    else:
        log = open("logs/logs.txt","a+") 
except:
    os.mkdir("logs")
    extension = "csv" if csv_format else "txt"
    log_path = f"logs/logs.{extension}"
    log = open(log_path,"w+")
    log.close()
    log = open(log_path,"a+")


def get_time():
    return datetime.datetime.now()

def on_created(event):
    print(f"created, {event.src_path}, {get_time()}\n")
    process_new_file(event)
    log.write(f"created, {event.src_path}, {get_time()}\n")
    log.flush()

def on_deleted(event):
    log.write(f"deleted, {event.src_path}, {get_time()}\n")
    log.flush()

def on_modified(event):    
    #new_path = shutil.copy(event.src_path,f"APMC\{to_copy_stack[0]}")
    filename = str(event.src_path)
    filename = filename.split("\\")
    filename = filename[len(filename)-1]
    camera_folder = filename[5:13]+"_"+filename[13:17]
    print(f"modified, {event.src_path}, {get_time()}\n")
    terminal(f'copy {event.src_path} APMC\\{gen_filename(event.src_path)}')
    trim_one_minute(event.src_path,f"APMC\camera0{filename[2:4]}\\{camera_folder}")
    log.write(f"modified, {event.src_path}, {get_time()}\n")
    log.flush()

def on_moved(event):
    log.write(f" Moved, {event.src_path} to {event.dest_path}, {get_time()}\n")
    log.flush()
            
def process_new_file(event):
    filename = str(event.src_path)
    filename = filename.split("\\")
    filename = filename[len(filename)-1]
    #print(filename)
    extension = filename.split(".")
    extension = extension[len(extension)-1]
    #print(f"the extension is {extension}")
    old_path = event.src_path
    if(extension in file_types):
        if(filename.startswith("ch")):
            new_filename =  gen_filename(event.src_path)
            
            try:
                #new_path = shutil.copy2(old_path,f"APMC\{new_filename}")
                to_copy_stack = new_filename
                terminal(f'copy {event.src_path} APMC\\{new_filename}')
                
            except:
                #to_copy_stack.append(new_filename)
                print('error copying to ',f"APMC\{new_filename}")
                #print(len(to_copy_stack))
                #copy_file_stack(event,new_filename)
            try:
                os.mkdir(f"APMC\camera0{filename[2:4]}")
            except:
                print("folder APMC already exist")
            try:
                camera_folder = filename[5:13]+"_"+filename[13:17]
                os.mkdir(f"APMC\camera0{filename[2:4]}\\{camera_folder}")
            except:
                print(f"folder {camera_folder} already exist")
                
            
            #print(new_path)

def terminal(command):
    #only for copying files
    if(os.name == 'nt'):
        print('Detected Windows OS')
        os.system(command)
    else:
        command = "cp "+command[5:]
        os.system("")

if __name__ == "__main__":
    curr_time = get_time()
    patterns = "*"
    ignore_patterns = "*\logs.txt", "*\logs.csv","*\logs","*.py"
    ignore_directories = False
    case_sensitive = True
 
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved
    path = ".\drive"
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
    