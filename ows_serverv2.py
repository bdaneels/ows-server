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
import json

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

def get_uploader_config(script_name):
    """Haal uploader configuratie op voor een specifiek script, of de default."""
    section_name = f'uploader_{script_name}'
    if section_name in settings:
        return settings[section_name], section_name
    return settings['uploader'], 'uploader'

def is_multi_field_uploader(config_section):
    """Check of de uploader meerdere specifieke velden heeft."""
    return 'upload_1_name' in settings[config_section]

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
    script_name = app.storage.user.get('script', '')
    uploader_config, config_section = get_uploader_config(script_name)
    
    # Check of dit een multi-field uploader is
    if is_multi_field_uploader(config_section):
        # Specifieke upload pagina voor scripts met benoemde velden
        render_multi_field_upload(script_name, config_section)
    else:
        # Standaard upload pagina
        render_standard_upload(script_name, config_section)

def render_multi_field_upload(script_name, config_section):
    """Render upload pagina met specifieke benoemde upload velden."""
    config = settings[config_section]
    uploaded_files = {}
    
    def handle_specific_upload(e: events.UploadEventArguments, field_name: str):
        handle_upload(e)
        uploaded_files[field_name] = e.name
        log.debug(f'Uploaded {field_name}: {e.name}')
        check_all_uploaded()
    
    def check_all_uploaded():
        # Tel hoeveel upload velden er zijn
        field_count = 1
        while f'upload_{field_count}_name' in config:
            field_count += 1
        field_count -= 1
        
        if len(uploaded_files) == field_count:
            next_btn.enable()
        else:
            next_btn.disable()
    
    def file_rejected(e):
        ui.notify(f'Bestand is geweigerd (te groot)')
    
    def go_to_run():
        # Sla de bestanden op in de juiste volgorde
        files = []
        field_names = []
        i = 1
        while f'upload_{i}_name' in config:
            field_name = config[f'upload_{i}_name']
            field_names.append(field_name)
            if field_name in uploaded_files:
                files.append(uploaded_files[field_name])
            i += 1
        
        app.storage.user['files'] = files
        app.storage.user['file_names'] = field_names
        ui.navigate.to('/run_script')
    
    # UI
    create_header()
    ui.label(f'Script: {script_name}').classes('text-xl font-bold')
    
    max_size = safe_eval(config.get('max_file_size', '1048576'))
    
    # Maak upload velden aan voor elk benoemd veld
    i = 1
    while f'upload_{i}_name' in config:
        field_name = config[f'upload_{i}_name']
        field_label = config.get(f'upload_{i}_label', f'Upload bestand {i}')
        
        with ui.card().classes('w-full'):
            ui.label(field_label).classes('font-semibold')
            # Gebruik een closure om de juiste field_name te capturen
            ui.upload(
                on_upload=lambda e, fn=field_name: handle_specific_upload(e, fn),
                max_file_size=max_size,
                max_files=1,
                on_rejected=file_rejected,
                multiple=False
            ).props('accept=*').classes('max-w-full')
        i += 1
    
    next_btn = ui.button('Volgende', on_click=go_to_run)
    next_btn.disable()

def render_standard_upload(script_name, config_section):
    """Render standaard upload pagina met file selectie grid."""
    config = settings[config_section]
    
    columns = [
        {'field': 'filename', 'checkboxSelection': True,
         'editable': False, 'sortable': True},
        {'field': 'size', 'editable': False, 'sortable': True},
    ]
    rows = []
    
    def update_aggrid():
        upload_dir = settings['paths']['upload']
        if not os.path.exists(upload_dir):
            ui.notify(f'specified upload dir {upload_dir} does not exist!')
            return
        rows.clear()
        for fentry, fstat in get_files_dir(upload_dir):
            grid_line = {'filename': fentry.name, 'size': fstat.st_size}
            rows.append(grid_line)
        aggrid.update()

    async def get_selected_rows():
        files = []
        sel_rows = await aggrid.get_selected_rows()
        max_files = int(config.get('max_files', 2))
        if len(sel_rows) == max_files:
            for row in sel_rows:
                ui.notify(f"{row['filename']}")
                files.append(row['filename'])
            app.storage.user['files'] = files
            ui.navigate.to('/run_script')
        elif len(sel_rows) == 0:
            ui.notify('No rows selected.')
        else:
            ui.notify(f'Je moet {max_files} bestanden selecteren')

    def file_upload(e):
        handle_upload(e)

    def file_rejected(e):
        ui.notify(f'file has been rejected (size)')

    # UI
    bytes = safe_eval(config['max_file_size'])
    create_header()
    log.debug(f"max_file_size for uploads-> {bytes} bytes")
    ui.label(f"{script_name}")
    ui.upload(
        on_upload=file_upload,
        max_file_size=safe_eval(config['max_file_size']),
        max_files=int(config.get('max_files', 2)),
        label=config.get('label', 'Upload bestanden'),
        on_multi_upload=update_aggrid,
        on_rejected=file_rejected,
        multiple=True
    ).props('accept=*').classes('max-w-full')

    with ui.card():
        ui.label(f"Selecteer {config.get('max_files', 2)} bestanden")
        aggrid = ui.aggrid({
            'columnDefs': columns,
            'rowData': rows,
            'rowSelection': 'multiple',
        })
    btn = ui.button('Next', on_click=get_selected_rows)
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
            self.warnings = []
            
    def get_check_path_script(script):
        fpath = settings['scripts'][script]
        if not os.path.exists(fpath):
            ui.notify(f'script full name {fpath}  not found!')
            return None
        return fpath
    
    def parse_ui_output(stdout_text):
        """Extract structured UI data from script output."""
        try:
            start_marker = "---UI_OUTPUT_START---"
            end_marker = "---UI_OUTPUT_END---"
            if start_marker in stdout_text and end_marker in stdout_text:
                start = stdout_text.index(start_marker) + len(start_marker)
                end = stdout_text.index(end_marker)
                json_str = stdout_text[start:end].strip()
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            log.error(f"Failed to parse UI output: {e}")
        return None
            
    async def start_script(script, fp_script, fp_fileA, fp_fileB):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        user =  app.storage.user['user']
        fn_out = f'{user}_{timestamp}.xlsx'
        fp_out = add_output_path(fn_out)

        cmd = ['python3', f'{fp_script}', f'{fp_fileA}', f'{fp_fileB}', f'{fp_out}']
        if settings['general']['debug']:
            cmd += ['--verbose']
        log.debug(f"command -> {cmd}")
        cmd_lbl.text = f"{cmd}"
        spinner.set_visibility(True)
        checkmark.visible = False
        stdout, stderr = await run_subprocess(cmd)
        
        stdout_text = stdout.decode()
        stderr_text = stderr.decode()
        
        cscript.fileOut = fp_out
        cscript.button_enabled = True
        spinner.set_visibility(False)
        checkmark.visible = True
        
        log.debug(f'Standard Output: {stdout_text}')
        log.debug(f'Standard Error: {stderr_text}')
        
        # Parse structured output for UI
        ui_data = parse_ui_output(stdout_text)
        if ui_data and 'warnings' in ui_data:
            cscript.warnings = ui_data['warnings']
            warnings_grid.options['rowData'] = ui_data['warnings']
            warnings_grid.update()
            results_expansion.open()
            
            # Show summary if available
            if 'summary' in ui_data:
                summary_label.text = f"Totaal: {ui_data['summary'].get('total_warnings', 0)} waarschuwingen"
        
        out.content = f'```\n{stdout_text}\n```'
        error.content = f'```\n{stderr_text}\n```'
        
        if rem_compared_files.value:
            log.debug("removing compared files...")
            if os.path.exists(fp_fileA):
                os.remove(fp_fileA)
            if os.path.exists(fp_fileB):
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
    #and we add paths to the selected files
    fp_fileA =  add_upload_path(fileA)
    fp_fileB = add_upload_path(fileB)
    
    with ui.expansion('File details', icon='info').classes('w-full') as details:
        ui.label(f'script -> {fp_script}')
        ui.label(f'fp_file 1 -> {fp_fileA}')
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
        spinner = ui.spinner(size='lg')
        spinner.visible = False
        checkmark = ui.icon('check_circle', size='lg').classes('text-green-500')
        checkmark.visible = False
        d = ui.button('Download', on_click=lambda: ui.download.file(f'{cscript.fileOut}'))
        d.bind_enabled_from(cscript, 'button_enabled')
        
        # New: Script results expansion with AG Grid
        with ui.expansion('Script resultaten', icon='warning').classes('w-full').props('default-opened') as results_expansion:
            summary_label = ui.label('Nog geen resultaten')
            warnings_columns = [
                {'field': 'student_id', 'headerName': 'Student ID', 'sortable': True},
                {'field': 'voornaam', 'headerName': 'Voornaam', 'sortable': True},
                {'field': 'achternaam', 'headerName': 'Achternaam', 'sortable': True},
                {'field': 'email', 'headerName': 'Email', 'sortable': True},
                {'field': 'waarschuwing', 'headerName': 'Waarschuwing', 'sortable': True, 'flex': 2},
            ]
            warnings_grid = ui.aggrid({
                'columnDefs': warnings_columns,
                'rowData': [],
                'domLayout': 'autoHeight',
            }).classes('w-full')
        
        with ui.expansion('Terminal output', icon='terminal').classes('w-full'):
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

