class RetinalGanglionCell(object):
    # Constants
    TYPE_ON = 1
    TYPE_OFF = -1

    def __init__(self, cell_id, cell_position, cell_type):
        self.id = cell_id
        self.x = cell_position[0]
        self.y = cell_position[1]
        self.type = cell_type
