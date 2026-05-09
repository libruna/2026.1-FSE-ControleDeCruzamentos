import time

class TrafficLight:

    def __init__(self, name, initial_state, min_green, max_green, min_yellow, min_red):
        self.name = name
        self.state = initial_state

        self.state_start_time = 0
        self.green_mintime = min_green
        self.green_maxtime = max_green
        self.yellow_mintime = min_yellow
        self.red_mintime = min_red

        self.waiting = False

    def _change_state(self, time, state):
        self.state = state
        self.state_start_time = time
        self.waiting = False
        
    def execute(self, time, block_green = False):

        state_duration = time - self.state_start_time

        if self.state == 'green':
            if state_duration >= self.green_maxtime:
                self._change_state(time, 'yellow')
            elif state_duration >= self.green_mintime and self.waiting:
                self._change_state(time, 'yellow')
                print(f'travessia antecipada em {self.name}({state_duration:.2f}s)')

        elif self.state == 'yellow' and state_duration >= self.yellow_mintime:
            self._change_state(time, 'red')

        elif self.state == 'red' and state_duration >= self.red_mintime and not block_green:
            self._change_state(time, 'green')

    def queue_pedestrian(self):
        self.waiting = True
        print(f'travessia requisitada em {self.name}')
