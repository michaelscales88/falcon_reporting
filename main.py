from automated_sla_tool.src.SlaFiles import SlaFiles
from automated_sla_tool.utilities.GenericUi import GenericUi as UI


def main():
    my_ui = UI()
    my_ui.object = SlaFiles()
    my_ui.run()

if __name__ == '__main__':
    main()
