class TrafficLight:

    def __init__(self, name, initial_state, min_green, max_green, min_yellow, red_total):
        self.name = name
        self.state = initial_state

        self.state_start_time = 0
        self.green_mintime = min_green
        self.green_maxtime = max_green
        self.yellow_mintime = min_yellow
        self.red_total = red_total
        self.last_block = 0

        self.waiting = False

    def _change_state(self, time, state):
        self.state = state
        self.state_start_time = time
        self.waiting = False
        
    def execute(self, time, block_green = False, force=''):
        if force == 'open' and (self.state == 'yellow' or (self.state == 'red' and not block_green)):
            print(f'forcing {self.name} {force}, was {self.state}')
            self._change_state(time, 'green')
        elif force == 'close' and self.state == 'green':
            print(f'forcing {self.name} {force}, was {self.state}')
            self._change_state(time, 'yellow')
            


        state_duration = time - self.state_start_time

        if self.state == 'green':
            if force == 'open':
                pass
            elif state_duration >= self.green_maxtime:
                self._change_state(time, 'yellow')
            elif state_duration >= self.green_mintime and self.waiting:
                self._change_state(time, 'yellow')
                print(f'[INFO] travessia antecipada em {self.name}({state_duration:.2f}s)')

        elif self.state == 'yellow' and state_duration >= self.yellow_mintime:
            self._change_state(time, 'red')

        elif self.state == 'red':
            if state_duration >= self.red_total:
                if block_green:
                    self.last_block = time
                elif force == 'close':
                    pass
                else:
                    if (time - self.last_block) >= self.red_total:
                        self._change_state(time, 'green')

        # elif self.state == 'red' and state_duration >= self.red_total and not block_green:
            # self._change_state(time, 'green')

    def queue_pedestrian(self, canal = None):
        self.waiting = True
        print(f'[INFO] travessia requisitada em {self.name}')
