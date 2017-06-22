import sys
import os
import argparse
import pandas as pd
import xml.etree.ElementTree as et
from RetinalGanglionCell import RetinalGanglionCell
import logging

# Main script
if __name__ == '__main__':
    # Check Python version
    if sys.version_info[0] < 3:
        raise TypeError('This program must be executed with Python 3')

    # Argument parser
    parser = argparse.ArgumentParser(description='OpenCV-Retina simulator')
    parser.add_argument('--data', metavar='data', type=str, nargs='?', help='Input data files folder')

    args = parser.parse_args()
    if args.data is None:
        raise 'ERROR: the arg --data is mandatory [path of the input data]'
    data_path = os.path.join(args.data, '')

    # Logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Read retina.xml file
    logger.info('Start reading retina.xml file')
    tree = et.parse(data_path + 'retina.xml')
    root = tree.getroot()

    # Dictionary of all rgc
    retinal_ganglion_cells = {}

    # Build retinal ganglion cells data information
    logger.info('Start building retinal ganglion cells data information')
    for rgc_layer in root.iter('ganglion-layer'):
        rgc_type = rgc_layer.get('sign')
        for unit in rgc_layer.iter('unit'):
            id = unit.get('mvaspike-id')
            x = unit.get('x-offset__deg')
            y = unit.get('y-offset__deg')
            rgc = RetinalGanglionCell(cell_id=id, cell_position=(x, y), cell_type=rgc_type)
            retinal_ganglion_cells[id] = rgc

    # Read spikes.spk file
    logger.info('Start reading spikes.spk file')
    spike_data = pd.read_csv(data_path + 'spikes.spk', sep='\s+', header=None, names=['ID', 'TIME'])

    logger.info('End of execution of ' + __file__)
