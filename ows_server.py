# -*- mode: python; indent-tabs-mode: nil; python-indent-offset: 4 -*-
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
from pprint import pformat

#read a file with configuration settings
#settings are in compare_it.ini file
settings = configparser.ConfigParser()
#by setting the next, the values become dynamic (use of ${})
settings._interpolation = configparser.ExtendedInterpolation()
if os.path.exists('ows.ini'):
    settings.read_file(open('ows.ini'))
else:
    print("no configuration file found (ows.ini)")
    exit

def add_script_path(fname):
    script_dir = settings['paths']['script']
    if not os.path.exists(script_dir):
        ui.notify(f'specified script dir {script_dir} does not exist!')
        return
    fname_wpath = os.path.join(script_dir, fname)
    return fname_wpath

def add_upload_path(fname):
    upload_dir = settings['paths']['upload']
    if not os.path.exists(upload_dir):
        ui.notify(f'specified upload dir {upload_dir} does not exist!')
        return
    fname_wpath = os.path.join(upload_dir, fname)
    return fname_wpath

def handle_upload(e: events.UploadEventArguments):
    print('handle upload')
    upload_dir = settings['paths']['upload']
    if not os.path.exists(upload_dir):
        ui.notify(f'specified upload dir {upload_dir} does not exist!')
        return
    #pprint.pp(e)
    fname = e.name
    ftype = e.type
    print(f'uploaded file name -> {fname} type {ftype}')
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
                print(entry.name)
                fstat = entry.stat()
                print(fstat.st_size)
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
                  }
    
    with ui.header(elevated=True).style('background-color: #3874c8') \
                                 .classes('items-center justify-between'):
        ui.label('OWS')
        with ui.row().classes('max-[1050px]:hidden'):
            for title_, target in menu_items.items():
                ui.link(title_, target).classes(replace='text-lg text-white')
                
@ui.page('/sel_script')
def page_sel_script():
    _columns = [
        {'field': 'filename', 'checkboxSelection': True,
         'editable': False, 'sortable': True},
        {'field': 'size', 'editable': False, 'sortable' : True},
    ]

    _rows = [
    ]

    def update_aggrid():
        script_dir = settings['paths']['script']
        if not os.path.exists(script_dir):
            ui.notify(f'specified script dir {script_dir} does not exist!')
            return
        grid_line = {}
        _rows.clear()
        for fentry, fstat in get_files_dir(script_dir):
            grid_line = {'filename':fentry.name, 'size':fstat.st_size}
            print(f"{grid_line}")
            _rows.append(grid_line)
        _aggrid.update()

    async def get_selected_row():
        row = await _aggrid.get_selected_row()
        if row:
            ui.notify(f"{row['filename']}")
            ui.navigate.to(f"/upl_files/{row['filename']}")
        else:
            ui.notify('No row selected!')
    #UI         
    create_header()
    _aggrid = ui.aggrid({
        'columnDefs': _columns,
        'rowData': _rows,
        'rowSelection': 'single',       
    })
    #ui.button('Refresh', on_click=update_aggrid)
    ui.button('Next',on_click=get_selected_row)    
    update_aggrid()
    
@ui.page('/upl_files/{sel_script}')
def page_upl_files(sel_script):
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
            print(f"{grid_line}")
            rows.append(grid_line)
        aggrid.update()

    async def get_selected_rows():
        files = []
        sel_rows = await aggrid.get_selected_rows()
        if len(sel_rows) == 2:
            for row in sel_rows:
                ui.notify(f"{row['filename']}")
                files.append(row['filename'])
            ui.navigate.to(f'/run_script/{sel_script}/{files[0]}/{files[1]}/')
        elif len(sel_rows) == 0:
            ui.notify('No rows selected.')
        else:
            ui.notify('you must select 2 files')
            
    def file_upload(e):
        handle_upload(e)
        update_aggrid()

    #UI
    create_header()            
    ui.label(f'{sel_script}')        
    ui.upload(on_upload=file_upload).props('accept=*').classes('max-w-full')

    aggrid = ui.aggrid({
        'columnDefs': columns,
        'rowData': rows,
        'rowSelection': 'multiple',       
    })
    #ui.button('Refresh', on_click=update_aggrid)
    ui.button('Next',on_click=get_selected_rows)
    update_aggrid()

@ui.page('/run_script/{script}/{fileA}/{fileB}')
def page_run_script(script, fileA, fileB):

    async def start_script(script, fileA, fileB):
        fp_script = add_script_path(script)
        fp_fileA = add_upload_path(fileA)
        fp_fileB = add_upload_path(fileB)

        #check if all files exist
        cmd = ['python3', f'{fp_script}', f'{fp_fileA}', f'{fp_fileB}', 'out.csv']
        print(f"command -> {cmd}")
        cmd_lbl.text = f"{cmd}"
        spinner.set_visibility(True)
        stdout, stderr = await run_subprocess(cmd)
        spinner.set_visibility(False)
        print(f'Standard Output: {stdout.decode()}',
              f'Standard Error: {stderr.decode()}')
        out.content = f'```\n{stdout.decode()}\n```'
        error.content = f'```\n{stderr.decode()}\n```'
        if rem_compared_files.value:
            print("removing compared files...")
            os.remove(fp_fileA)
            os.remove(fp_fileB)
        else:
            print("nothing to remove")
            
    #UI
    create_header()
    ui.label(f'{script}')
    ui.label(f'{fileA}')
    ui.label(f'{fileB}')
    cmd_lbl = ui.label()
    rem_compared_files = ui.checkbox('remove 2 files (xlsx) after processing')
    rem_compared_files.value = True
    ui.button('Start script', on_click=lambda e: start_script(script, fileA, fileB))
    spinner = ui.spinner(size='lg') # .classes('absolute-center')
    spinner.visible = False
    ui.label('stderr')
    with ui.card() as err_card:       
        error = ui.markdown()
    ui.label('stdout')
    with ui.card() as out_card:
        out = ui.markdown()

@ui.page('/')
def page_index():
    create_header()
    ui.html('Some explanation or communication for <strong>users</strong>')
    ui.button('Select a script', on_click=lambda e: ui.navigate.to('/sel_script'))

hostname = settings['general']['hostname']
sock_hostname = socket.gethostname()
if sock_hostname == hostname:
    print("running on the server...")
    ui.run(reload=False, host='0.0.0.0')
else:
    print("running locally...")
    ui.run()    

