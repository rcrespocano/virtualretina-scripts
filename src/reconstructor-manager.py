import sys
import os
import argparse
import logging
import cv2
import datetime
import numpy as np
import pandas as pd
import VideoManager as vm
import xml.etree.ElementTree as et
from RetinalGanglionCell import RetinalGanglionCell

# Main script
if __name__ == '__main__':
    # Check Python version
    if sys.version_info[0] < 3:
        raise TypeError('This program must be executed with Python 3')

    # Argument parser
    parser = argparse.ArgumentParser(description='OpenCV-Retina simulator')
    parser.add_argument('--data', metavar='data', type=str, nargs='?', help='Input data files folder')
    parser.add_argument('--fps', metavar='fps', type=float, nargs='?', help='Frames per second (fps)')
    parser.add_argument('--ppd', metavar='ppd', type=float, nargs='?', help='Pixels per degree')

    args = parser.parse_args()
    if args.data is None:
        raise TypeError('ERROR: the arg --data is mandatory [Path of the input data]')
    if args.fps is None:
        raise TypeError('ERROR: the arg --fps is mandatory [Frames per second (fps)]')
    if args.ppd is None:
        raise TypeError('ERROR: the arg --ppd is mandatory [Pixels per degree (ppd)]')

    # Parameters
    data_path = os.path.join(args.data, '')
    fps = args.fps
    pixels_per_degree = args.ppd

    # Logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Output
    root_output_folder = 'output/'
    output_file = 'outputvr_'
    output_ext = '.tif'
    output_video_ext = '.avi'
    output_folder = data_path + root_output_folder + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '/'

    logger.info('Create output folder (root) if not exists.')
    if not os.path.exists(root_output_folder):
        os.makedirs(root_output_folder)

    logger.info('Create simulation directory: ' + output_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Read retina.xml file
    logger.info('Start reading retina.xml file')
    tree = et.parse(data_path + 'retina.xml')
    root = tree.getroot()

    # Dictionary of all rgc
    retinal_ganglion_cells = {}

    # RGC max values
    rgc_max_x = 0.0
    rgc_max_y = 0.0

    # Build retinal ganglion cells data information
    logger.info('Start building retinal ganglion cells data information')
    for rgc_layer in root.iter('ganglion-layer'):
        _rgc_type = int(rgc_layer.get('sign'))
        for unit in rgc_layer.iter('unit'):
            _id = int(unit.get('mvaspike-id'))
            _x = float(unit.get('x-offset__deg'))
            _y = float(unit.get('y-offset__deg'))
            _rgc = RetinalGanglionCell(cell_id=_id, cell_position=(_x, _y), cell_type=_rgc_type)
            retinal_ganglion_cells[_id] = _rgc

            rgc_max_x = max(rgc_max_x, abs(_x))
            rgc_max_y = max(rgc_max_y, abs(_y))

    # Read spikes.spk file
    logger.info('Start reading spikes.spk file')
    spike_data = pd.read_csv(data_path + 'spikes.spk', sep='\s+', header=None, names=['ID', 'TIME'])

    # Output frame parameters
    white = 255
    gray = 75
    black = 0
    time_step = 1 / fps
    time_counter = 0
    frame_id = 0
    image_size = (int(rgc_max_x * 2 * pixels_per_degree) + 1, int(rgc_max_y * 2 * pixels_per_degree) + 1)
    
    # Frame with all data
    stimulus = np.full(image_size, gray, dtype='uint8')

    logger.info('Processing spike data. This could take some time.')
    while time_counter < max(spike_data['TIME']):
        mask = (spike_data['TIME'] >= time_counter) & (spike_data['TIME'] < time_counter + time_step)
        sub_data = spike_data.loc[mask]

        for index, row in sub_data.iterrows():
            _id = int(row['ID'])
            _rgc = retinal_ganglion_cells[_id]
            _x = int((_rgc.x + rgc_max_x) * pixels_per_degree)
            _y = int((_rgc.y + rgc_max_y) * pixels_per_degree)
            stimulus[_x, _y] = white if _rgc.type == RetinalGanglionCell.TYPE_ON else black

        time_counter += time_step

        # Stimulus frame
        frame_id += 1
        cv2.imwrite(output_folder + output_file + str(frame_id) + output_ext, stimulus)

        # Restart stimulus frame
        stimulus = np.full(image_size, gray, dtype='uint8')

    logger.info('The simulation has been successfully completed')

    # Create output video
    logger.info('Creating output video files')
    vm.build_video(output_folder, output_video_ext, output_file, output_ext, fps)

    logger.info('The process has been successfully completed')
    logger.info('End of execution of ' + __file__)
