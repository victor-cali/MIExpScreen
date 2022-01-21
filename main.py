from os import listdir
from os.path import isfile, join, splitext
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
import numpy as np
from pylsl import StreamInfo, StreamOutlet

info = StreamInfo('MIExpScreenStim', 'Markers', 1, 0, 'int32', 'MIExpScreenApp')
outlet = StreamOutlet(info)

class SettingsWindow(Screen):
    def __init__(self, **kw):
        super(SettingsWindow, self).__init__(**kw)    

class ExperimentWindow(Screen):

    sound = SoundLoader.load('beep.wav')
    rng = np.random.default_rng()

    def __init__(self, settings, **kw):
        super(ExperimentWindow, self).__init__(**kw)
        self.classes_paths = settings['classes']
        self.low_lim, self.top_lim = settings['break_interval']
        self.mi_len = settings['mi_duration']
        self.trials_num = settings['trials_num']

    def on_enter(self):
        outlet.push_sample([0])
        classes = self.classes_paths.keys()
        trials = self.rng.permutation([c for _ in range(self.trials_num) for c in classes if c != 0])
        breaks = self.rng.integers(self.low_lim, self.top_lim, self.trials_num*len(classes), endpoint = True)
        self.trials = list(trials)
        self.breaks = list(breaks/10)
        Clock.schedule_once(self.play_sound, 9)
        Clock.schedule_once(self.next_state, 10)
        print(self.trials)
        return super().on_enter()

    def play_sound(self, dt):
        self.sound.play()
    
    def next_state(self,dt):
        try:
            img_num = self.trials.pop()
            screen_img_src = self.classes_paths[img_num]
            self.ids.screen_img.source = screen_img_src
            outlet.push_sample([img_num])
            Clock.schedule_once(self.set_break_time, self.mi_len)
        except:
            pass
    
    def set_break_time(self,dt):
        try:
            screen_img_src = self.classes_paths[0]
            outlet.push_sample([0])
            self.ids.screen_img.source = screen_img_src
            break_time = self.breaks.pop() + self.mi_len
            Clock.schedule_once(self.play_sound, break_time - 1)
            Clock.schedule_once(self.next_state, break_time)
        except:
            pass

Builder.load_file('view.kv')

class MIExpScreenApp(App):
    sm = ScreenManager()
    def build(self):
        settings_window = SettingsWindow(name = "settings_window")
        self.sm.add_widget(settings_window)
        return self.sm

    def set_experiment(self):
        screen = self.root.get_screen('settings_window')
        path = screen.ids.file_chooser.selection[0]

        selected_images = [f for f in listdir(path) if isfile(join(path, f))]
        try:
            classes = [int(splitext(f)[0]) for f in selected_images]
            paths = [f'{path}\\{f}' for f in selected_images]
        except:
            classes = list()
            paths = list()
        classes_paths = dict(zip(classes, paths))
        assert classes_paths, "Classes not selected"
        assert screen.ids.mi_duration.text, "Field empty"
        assert screen.ids.trials_num.text, "Field empty"
        assert screen.ids.low_lim.text, "Field empty"
        assert screen.ids.top_lim.text, "Field empty"
        try:
            low_lim = float(screen.ids.low_lim.text)*10
            top_lim = float(screen.ids.top_lim.text)*10
            mi_duration = float(screen.ids.mi_duration.text)
            trials_num = int(screen.ids.trials_num.text)
        except:
            raise ValueError("Values are not valid")

        settings = {
            'classes': classes_paths,
            'break_interval': (low_lim, top_lim),
            'mi_duration': mi_duration,
            'trials_num': trials_num
        }

        experiment_window = ExperimentWindow(settings, name = "experiment_window")
        self.sm.add_widget(experiment_window)

        screen = self.root.get_screen('experiment_window')
        screen.ids.screen_img.source = classes_paths[0]
        self.root.current = "experiment_window"


        
if __name__ == '__main__':
    MIExpScreenApp().run()