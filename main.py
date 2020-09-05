import InputController
import DataController
import OutputController

inputController = InputController.InputController()
inputController.read_user_input()

dataController = DataController.DataController()
dataController.convert_md_to_html()

outputController = OutputController.OutputController()
outputController.print_formatted_text()
