from os import listdir
from os.path import isfile, join, splitext
import kivy
from kivy.app import App
from kivy.uix.widget import Widget


class MyLayout(Widget):
    pass

class MIExpScreenApp(App):

    classes_paths = dict()
    
    def build(self):
        return MyLayout()

    def get_selection(self,path):
        selected_images = [f for f in listdir(path[0]) if isfile(join(path[0], f))]
        try:
            classes = [int(splitext(f)[0]) for f in selected_images]
            paths = [f'{path[0]}\\{f}' for f in selected_images]
        except:
            classes = list()
            paths = list()
        self.classes_paths = dict(zip(classes, paths))


if __name__ == '__main__':
    MIExpScreenApp().run()