from nicegui import ui


scripts = ['test', 'startpaketten']

for script in scripts:
    link = f'/file_upl/sel_script={script}'
    print(link)
    # Create a button and disable it
    button = ui.button(f'{script}', on_click=lambda link=link: ui.notify(link))



# Start the NiceGUI app
ui.run()
