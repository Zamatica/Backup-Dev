import logging
import json
import os
import psutil
import shutil
import time

with open('vars.json') as f:
    VARS = json.load(f)
backup_max = VARS["vars"]["backup_max"]
editor_name = VARS["vars"]["editor_name"]
editor_backup_time = VARS["vars"]["editor_backup_time"]
no_editor_backup_time = VARS["vars"]["no_editor_backup_time"]
log_max_size = VARS["vars"]["log_max_size"]
dirs = VARS["dirs"]

backups = os.listdir('backups/')
backup_count = VARS['backup_count']

backup_list, boolean = [], False
sleep_time = editor_backup_time

logging.basicConfig(filename='backup.log', filemode='a', format='%(asctime)s | %(levelname)s:  %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logging.info('')
logging.info('')
logging.info("---------------------------------------------")
logging.info("Starting backup system...")
logging.info('Loading variables...')
logging.info('Max File Size: ' + str(log_max_size))
logging.info('Max Number of Backups: ' + str(backup_max))
logging.info('Directories: ' + str(dirs))
logging.info('Editor: ' + editor_name)
logging.info('')


def error_pass(error='No Error'):
    with open('error.txt', 'w') as error_file:
        error_file.write(error)
        error_file.close()


def backup():
    try:
        global backup_count, backup_max, backup_list
        if backup_count >= backup_max:
            backup_count = 0
        if backup_count == 0:
            backup_count += 1
        for bak in os.listdir('backups/'):
            if int(bak[0]) == backup_count and bak[2:100] == bak[2:100]:
                logging.info("Replacing: " + bak)
        for directory in dirs:
            if directory != '':
                name = str(backup_count) + "_" + folder_name(directory)
                logging.info("Starting backup: " + name)
                backup_complete = shutil.make_archive(name, 'zip', directory)
                logging.info("Backup Complete. Moving...")
                with open('backups/'+name+'.zip.bak', 'w') as d:
                    backup_move = 'backups/'+name+'.zip.bak'
                    d.close()
                shutil.move(backup_complete, str(backup_move))
            else:
                logging.warning('========== BLANK DIRECTORY FOUND ==========')
        backup_count += 1
        VARS['backup_count'] = backup_count
        with open('vars.json', 'w+') as count_vars:
            count_vars.write(json.dumps(VARS, indent=2))
    except Exception as e:
        error_pass(str(e))
        os.system('popup_console.py 1')
        logging.exception(e)


def unique(values):
    output = []
    seen = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def folder_name(directory):
    return str(os.path.basename(os.path.normpath(directory)))


log_1 = 0


def log_editor():
    global log_1, boolean
    if boolean and log_1 == 1:
        logging.info(editor_name + " found.")
        log_1 = 0
    elif not boolean and log_1 == 0:
        logging.info(editor_name + " not found.")
        log_1 = 1


def backup_runtime():
    try:
        global boolean, log_1, sleep_time, backup_list, backup_count, backups
        check_time = sleep_time
        while True:
            if os.path.getsize('backup.log') >= log_max_size:
                with open('backup.log', 'w'):
                    pass
            programs_list = []
            for p in psutil.process_iter():
                try:
                    programs_list.append(p.name())
                except psutil.Error:
                    pass
            if editor_name in programs_list:
                boolean = True
                sleep_time = editor_backup_time
                log_editor()
                if check_time >= sleep_time:
                    logging.info(' ==== Backup Starting... ==== ')
                    logging.info(editor_name + ' Found - Backuping every ' + str(editor_backup_time) + ' seconds.')
                    backup()
                    logging.info("Done with Backup(s).")
                    check_time = 0
                else:
                    check_time += 1
                time.sleep(1)
            else:
                boolean = False
                sleep_time = no_editor_backup_time
                log_editor()
                if check_time == sleep_time:
                    logging.info(' ==== Backup Starting... ==== ')
                    logging.info(editor_name + ' Not Found - Backuping Every ' + str(no_editor_backup_time) + ' seconds.')
                    backup()
                    logging.info("Done with Backup(s).")
                    check_time = 0
                else:
                    check_time += 1
                time.sleep(1)
    except Exception as e:
        error_pass(str(e))
        os.system('popup_console.py 1')
        logging.exception(e)
if 'no_run' in dirs:
    error_pass("Remove no_run and add directories in vars.json")
    os.system('popup_console.py 1')
elif not dirs:
    error_pass("No directories found.")
    os.system('popup_console.py 1')
else:
    backup()
    backup_runtime()
