import PySimpleGUI as sg

def prompt_url():
    layout = [
              [sg.Text('Please enter the URL of the regulation')],
              [sg.Text('URL', size=(15, 1)), sg.InputText()],
              [sg.Submit(), sg.Cancel()]
             ]

    window = sg.Window('Simple data entry window').Layout(layout)
    button, values = window.Read()
    return values


def prompt_user():
    layout = [
        [sg.Text('Please enter username')],
        [sg.Text('User name', size=(15, 1)), sg.InputText()],
        [sg.Text('Password', size=(15, 1)), sg.InputText('', password_char='*')],
        [sg.Submit(), sg.Cancel()]
    ]

    window = sg.Window('Simple data entry window', layout)
    event, values = window.Read()
    return values
