from nicegui import ui

@ui.page('/')
def page():
    grid = ui.aggrid({
        'columnDefs': [
            {'headerName': 'Name', 'field': 'name', 'checkboxSelection': True},
            {'headerName': 'Age', 'field': 'age'},
        ],
        'rowData': [
            {'name': 'Alice', 'age': 18},
            {'name': 'Bob', 'age': 21},
            {'name': 'Carol', 'age': 42},
        ],
        'rowSelection': 'multiple',
    }).classes('max-h-40')

    async def output_selected_rows():
        rows = await grid.get_selected_rows()
        if rows:
            for row in rows:
                ui.notify(f"{row['name']}, {row['age']}")
            ui.navigate.to('/page2')
        else:
            ui.notify('No rows selected.')

    async def output_selected_row():
        row = await grid.get_selected_row()
        if row:
            ui.notify(f"{row['name']}, {row['age']}")
        else:
            ui.notify('No row selected!')

            
    ui.button('Output selected rows', on_click=output_selected_rows)
    ui.button('Output selected row', on_click=output_selected_row)
    
@ui.page('/page2')
def page2():
    ui.label('page2')
    
ui.run()
