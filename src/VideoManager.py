import cv2
from os import listdir
from os.path import isfile, join


# Function to build the output video with the processed frames
def build_video(_output_folder, _output_video_ext, _file_pattern, _file_ext, _fps):
    # Video codec
    _fourcc = cv2.VideoWriter_fourcc(*'XVID')

    _image_list = [f for f in listdir(_output_folder) if isfile(join(_output_folder, f))
                   and f.find(_file_pattern) >= 0 and f.find(_file_ext) > 0]
    _image_list.sort()

    # Video writer
    _tmp_image = cv2.imread(_output_folder + _image_list[0])
    _shape = _tmp_image.shape
    _writer = cv2.VideoWriter(_output_folder + _file_pattern + _output_video_ext, _fourcc, _fps, (_shape[1], _shape[0]))

    for _file_str in _image_list:
        _frame = cv2.imread(_output_folder + _file_str)
        _writer.write(_frame)

    _writer.release()
