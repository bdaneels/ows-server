#-*- mode: python; indent-tabs-mode: nil; python-indent-offset: 4 -*-
import sys
import argparse
import pandas as pd
import configparser
from io import StringIO
from nicegui import run, ui, app, binding, events
import asyncio
import re
import os
import socket
import datetime
import pprint
from pprint import pformat
from ows_logger import setup_logger

#read a file with configuration settings
#settings are in compare_it.ini file
settings = configparser.ConfigParser()
#by setting the next, the values become dynamic (use of ${})
settings._interpolation = configparser.ExtendedInterpolation()
if os.path.exists('ows.ini'):
    settings.read_file(open('ows.ini'))
    print(f"{settings}")
else:
    print("no configuration file found (ows.ini)")
    exit
    
log = setup_logger("ows-server", debug=settings['general']['debug'])

def safe_eval(expr):
    allowed = {'__builtins__': None}
    return eval(expr, allowed, {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3})

def add_script_path(fname):
    script_dir = settings['paths']['script']
    if not os.path.exists(script_dir):
        ui.notify(f'specified script dir {script_dir} does not exist!')
        return None
    fname_wpath = os.path.join(script_dir, fname)
    return fname_wpath

def add_upload_path(fname):
    upload_dir = settings['paths']['upload']
    if not os.path.exists(upload_dir):
        ui.notify(f'specified upload dir {upload_dir} does not exist!')
        return None
    fname_wpath = os.path.join(upload_dir, fname)
    if not os.path.exists(fname_wpath):
        ui.notify(f'specified file {fname_wpath} does not exist!')
        return None
    return fname_wpath

def add_output_path(fname):
    output_dir = settings['paths']['out']
    if not os.path.exists(output_dir):
        ui.notify(f'specified output dir {output_dir} does not exist!')
        return
    fname_wpath = os.path.join(output_dir, fname)
    return fname_wpath

def handle_upload(e: events.UploadEventArguments):
    log.info('handle upload')
    upload_dir = settings['paths']['upload']
    if not os.path.exists(upload_dir):
        ui.notify(f'specified upload dir {upload_dir} does not exist!')
        return
    #pprint.pp(e)
    fname = e.name
    ftype = e.type
    log.debug(f'uploaded file name -> {fname} type {ftype}')
    #allow csv or xlsx files only
    if re.search('csv', ftype):
        text = e.content.read().decode('utf-8')
        #save the file
        with open(f'{upload_dir}/{e.name}', 'w') as file:
            file.write(text)
    elif re.search('officedocument', ftype):
        btext = e.content.read()
        #save the file
        with open(f'{upload_dir}/{e.name}', 'wb') as file:
            file.write(btext)
    else:
        ui.notify(f'filetype {ftype} not allowed for upload')


def get_files_dir(adir):    
    with os.scandir(adir) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                #log.debug(entry.name)
                fstat = entry.stat()
                #log.debug(fstat.st_size)
                yield entry, fstat


async def run_subprocess(cmd):
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    return stdout, stderr
                
def create_header():
    menu_items = {'Home': '/',
                  'Select script': '/sel_script',
                  'Upload files': '/upl_files',
                  'Download files':'/dwl_files',
                  }
    with ui.header(elevated=True).style('background-color: #3874c8') \
                                 .classes('items-center justify-between'):
        ui.label(f"{settings['general']['header_label']}")
        ui.label().bind_text_from(app.storage.user, 'user')
        with ui.row().classes('max-[1050px]:hidden'):
            for title_, target in menu_items.items():
                ui.link(title_, target).classes(replace='text-lg text-white')
                
@ui.page('/sel_script')
def page_sel_script():

    def save_and_next(key):
        app.storage.user['script'] = key
        ui.navigate.to('/upl_files')
  
    #UI         
    create_header()
    for key in settings['scripts']:
        with ui.card():
            if key in settings['comment']:
                text = settings.get('comment', key)
                ui.markdown(f"{text}")
            #be carefull here, assign the variable link to an argument, otherwise
            #the link value will be the last value it has after the loop 
            ui.button(f'{key}', on_click=lambda key=key: save_and_next(key))
        

    
@ui.page('/upl_files')
def page_upl_files():
    columns = [
        {'field': 'filename', 'checkboxSelection': True,
         'editable': False, 'sortable': True},
        {'field': 'size', 'editable': False, 'sortable' : True},
    ]
    
    rows = [
    ]
    
    def update_aggrid():
        grid_line = {}
        upload_dir = settings['paths']['upload']
        if not os.path.exists(upload_dir):
            ui.notify(f'specified upload dir {upload_dir} does not exist!')
            return
        rows.clear()
        for fentry, fstat in get_files_dir(upload_dir):
            grid_line = {'filename':fentry.name, 'size':fstat.st_size}
            #print(f"{grid_line}")
            rows.append(grid_line)
        aggrid.update()

    async def get_selected_rows():
        #log.debug('in get_selected_rows')
        files = []
        sel_rows = await aggrid.get_selected_rows()
        if len(sel_rows) == 2:
            for row in sel_rows:
                ui.notify(f"{row['filename']}")                
                files.append(row['filename'])
            app.storage.user['files'] = files
            ui.navigate.to('/run_script')
        elif len(sel_rows) == 0:
            ui.notify('No rows selected.')
        else:
            ui.notify('you must select 2 files')
            
    def file_upload(e):
        handle_upload(e)

    def file_rejected(e):        
        ui.notify(f'file has been rejected (size)')

    #UI
    bytes = safe_eval(settings['uploader']['max_file_size'])
    create_header()
    log.debug(f"max_file_size for uploads-> {bytes} bytes")
    ui.label(f"{app.storage.user['script']}")        
    ui.upload(on_upload=file_upload,
              max_file_size = safe_eval(settings['uploader']['max_file_size']),
              max_files = settings['uploader']['max_files'],
              label = settings['uploader']['label'],
              on_multi_upload = update_aggrid,
              on_rejected = file_rejected,
              multiple= True).props('accept=*').classes('max-w-full')

    with ui.card():
        ui.label('Select the 2 files you want to compare')
        aggrid = ui.aggrid({
            'columnDefs': columns,
            'rowData': rows,
            'rowSelection': 'multiple',       
        })
    btn = ui.button('Next',on_click=get_selected_rows)
    #btn.enabled = False
    update_aggrid()

@ui.page('/dwl_files')
def page_dwl_files():
    columns = [
        {'field': 'filename', 'checkboxSelection': True,
         'editable': False, 'sortable': True},
        {'field': 'size', 'editable': False, 'sortable' : True},
    ]
    
    rows = [
    ]
    
    def update_aggrid():
        grid_line = {}
        out_dir = settings['paths']['out']
        if not os.path.exists(out_dir):
            ui.notify(f'specified out dir {out_dir} does not exist!')
            return
        rows.clear()
        for fentry, fstat in get_files_dir(out_dir):
            grid_line = {'filename':fentry.name, 'size':fstat.st_size}
            print(f"{grid_line}")
            rows.append(grid_line)
        aggrid.update()

    async def get_selected_rows(e):
        #pprint.pp(e.sender.text)        
        files = []
        sel_rows = await aggrid.get_selected_rows()
        if len(sel_rows) > 0:
            for row in sel_rows:
                ui.notify(f"{row['filename']}")
                fname = add_output_path(row['filename'])
                if e.sender.text == settings['general']['download_lbl']:
                    ui.download.file(fname)
                elif e.sender.text == settings['general']['delete_lbl']:
                    os.remove(fname)
            update_aggrid()
        elif len(sel_rows) == 0:
            ui.notify('No rows selected.')
                
    #UI
    create_header()            
    ui.button('Select all', on_click=lambda: aggrid.run_grid_method('selectAll'))
    with ui.card():
        ui.label('Select the files you want to download or delete')
        aggrid = ui.aggrid({
            'columnDefs': columns,
            'rowData': rows,
            'rowSelection': 'multiple',       
        })
    ui.button(settings['general']['download_lbl'], on_click=get_selected_rows)
    ui.button(settings['general']['delete_lbl'], on_click=get_selected_rows)
    update_aggrid()

    
@ui.page('/run_script')
def page_run_script():

    class CScript:
        def __init__(self):
            self.fileOut = ''
            self.button_enabled = False
            
    def get_check_path_script(script):
        fpath = settings['scripts'][script]
        if not os.path.exists(fpath):
            ui.notify(f'script full name {fpath}  not found!')
            return None
        return fpath
        
    async def start_script(script, fp_script, fp_fileA, fp_fileB):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        user =  app.storage.user['user']
        fn_out = f'{user}_{timestamp}.csv'
        fp_out = add_output_path(fn_out)

        #check if all files exist
        
        cmd = ['python3', f'{fp_script}', f'{fp_fileA}', f'{fp_fileB}', f'{fp_out}']
        if settings['general']['debug']:
            cmd += ['--verbose']
        log.debug(f"command -> {cmd}")
        cmd_lbl.text = f"{cmd}"
        spinner.set_visibility(True)
        stdout, stderr = await run_subprocess(cmd)
        cscript.fileOut = fp_out
        cscript.button_enabled = True
        spinner.set_visibility(False)
        log.debug(f'Standard Output: {stdout.decode()}')
        log.debug(f'Standard Error: {stderr.decode()}')
        out.content = f'```\n{stdout.decode()}\n```'
        error.content = f'```\n{stderr.decode()}\n```'
        if rem_compared_files.value:
            log.debug("removing compared files...")
            os.remove(fp_fileA)
            os.remove(fp_fileB)
        else:
            log.debug("nothing to remove")
            
    #UI
    cscript = CScript()
    log.debug(f'{cscript.fileOut}')
    log.debug(f'{cscript.button_enabled}')
    create_header()
    #get the selected parameters from storage
    script = app.storage.user['script']
    fileA =  app.storage.user['files'][0]
    fileB =  app.storage.user['files'][1]
    #here we get the real script name, and check if it exists
    fp_script = get_check_path_script(script)
    ui.label(f'script -> {fp_script}')
    #and we add paths to the selected files
    fp_fileA =  add_upload_path(fileA)
    ui.label(f'fp_file 1 -> {fp_fileA}')
    fp_fileB = add_upload_path(fileB)
    ui.label(f'fp_file 2 -> {fp_fileB}')
    ui.label().bind_text_from(cscript, 'fileOut',
                              backward=lambda text: f'output file -> {text}')
    cmd_lbl = ui.label()
    #check if all files exist!
    if fp_script and fp_fileA and fp_fileB:
        rem_compared_files = ui.checkbox('remove 2 files (xlsx) after processing')
        rem_compared_files.value = True
        ui.button('Start script', on_click=lambda e: \
                  start_script(script, fp_script, fp_fileA, fp_fileB))
        spinner = ui.spinner(size='lg') # .classes('absolute-center')
        spinner.visible = False
        d = ui.button('Download', on_click=lambda: ui.download.file(f'{cscript.fileOut}'))
        d.bind_enabled_from(cscript, 'button_enabled')
        ui.label('stderr')
        with ui.card() as err_card:       
            error = ui.markdown()
        ui.label('stdout')
        with ui.card() as out_card:
            out = ui.markdown()
    else:
        ui.notify('one of the specified files does not exist. Cannot continue!')
        ui.label('one of the specified files does not exist. Cannot continue!')


def store_user(value):
    ui.notify(f'saving user {value}')
    app.storage.user['user'] = value
        
@ui.page('/')
def page_index():
    user = None
    create_header()
    if 'index_page' in settings['general']:
        ui.markdown(f"{settings['general']['index_page']}")
    if 'users' in settings['general']:
        users = settings['general']['users'].split(',')
    log.debug(f'{users}')
    if 'user' in app.storage.user:
        user = app.storage.user['user']
        log.debug(f'user {user} is in app.storage.user')
    ui.select(options=users, with_input=True, label='select user', value = user,
              on_change=lambda e: store_user(e.value)).classes('w-40')
    ui.button('Select a script', on_click=lambda e: ui.navigate.to('/sel_script'))

hostname = settings['general']['hostname']
sock_hostname = socket.gethostname()
if sock_hostname == hostname:
    log.info("running on the server...")
    ui.run(reload=False, host='0.0.0.0', storage_secret=settings['general']['storage_secret'])
else:
    log.debug("running locally...")
    ui.run(storage_secret=settings['general']['storage_secret'])    

