import configparser
import imghdr
import os
import shutil
from datetime import date
from datetime import datetime
from pathlib import Path

from PIL import Image

USER_NAME = os.getenv("USER")
SWITCH_FILE_NAME = '.opened'

IMAGE_DATETIME_EXIF_KEYS = [36867, 36868, 306]

CONFIG_STRUCTURE = {
    'Paths': [
        'SourcePaths',
        'TargetPath',
    ],
    'Video': [
        'VideoTypes'
    ]
}


def assert_config(config_file):
    for section in CONFIG_STRUCTURE:
        if section not in config_file:
            raise Exception('Section {} is missing in config.ini'.format(section))
        for config_item in CONFIG_STRUCTURE[section]:
            if config_item not in config_file[section]:
                raise Exception('Item {}.{} is missing in config.ini'.format(section, config_item))


def get_config_file_path():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini')


def get_configuration():
    config_file = configparser.ConfigParser()
    if not config_file.read(get_config_file_path()):
        raise Exception('File config.ini does not exist in project root directory')
    assert_config(config_file)
    return config_file


config = get_configuration()


def get_source_paths():
    paths = config['Paths']['SourcePaths'].split(',')
    return [path.format(user_name=USER_NAME).strip() for path in paths]


def get_target_path():
    path_str = config['Paths']['TargetPath'].format(user_name=USER_NAME)
    if not Path(path_str).is_dir():
        raise Exception('Target path {} does not exist'.format(path_str))
    return path_str


def get_supported_video_file_types():
    types = config['Video']['VideoTypes'].split(',')
    return [picture_type.strip() for picture_type in types]


def get_date_taken(file_path):
    if is_video(file_path):
        return get_date_taken_from_file_name(file_path)
    else:
        return get_date_taken_from_picture(file_path)


def get_date_taken_from_file_name(file_path):
    file_name = file_path.rsplit('/', 1)[1]
    if '20' not in file_name:
        return None

    date_string = '20' + file_name.split('20', 1)[1][:6]
    return datetime.strptime(date_string, '%Y%m%d').date()


def get_date_taken_from_picture(file_path):
    def get_date_string_from_image(image_path):
        """returns string in format '2017:07:28 17:11:25'"""
        img_metadata = Image.open(image_path)._getexif()
        for datetime_key in IMAGE_DATETIME_EXIF_KEYS:
            if datetime_key in img_metadata:
                return img_metadata[datetime_key]

    def parse_day(dates):
        """ The third item in the list includes date and an hour -
        eg. '28 17' - this method returns only the day portion - eg. 28
        """
        return dates[2].split(' ')[0]

    date_taken_string = get_date_string_from_image(file_path)

    date_list = date_taken_string.split(':')

    year = int(date_list[0])
    month = int(date_list[1])
    day = int(parse_day(date_list))

    return date(year, month, day)


def get_file_type(file_path):
    """fetch the file suffix from the file name"""
    file_suffix = os.path.splitext(file_path)[1]
    if file_suffix[0] != '.':
        return None
    return file_suffix[1:]


def log(msg):
    print('{} - {}'.format(str(datetime.now()), msg))


def main():
    for src_path_str in get_source_paths():
        log('Processing path {}'.format(src_path_str))
        card_path = Path(src_path_str)

        if not card_path.is_dir():
            log('Path {} is not available'.format(src_path_str))
            continue

        target_path = get_target_path()

        for media_file_path in card_path.glob('*'):

            media_file_path_string = str(media_file_path)
            if not is_picture(media_file_path_string) and not is_video(media_file_path_string):
                log('skipping file: ' + media_file_path_string)
                continue

            log('Processing file: ' + media_file_path_string)

            date_taken = get_date_taken(media_file_path_string)

            if not date_taken:
                raise Exception('Date could not be acquired from ' + media_file_path_string)

            date_folder_name = str(date_taken)

            target_year_folder = Path(os.path.join(target_path, str(date_taken.year)))
            if not target_year_folder.is_dir():
                target_year_folder.mkdir()

            target_date_folder = Path(os.path.join(str(target_year_folder), date_folder_name))
            switch_file_path = Path(os.path.join(str(target_date_folder), SWITCH_FILE_NAME))
            if not target_date_folder.is_dir():
                target_date_folder.mkdir()
                switch_file_path.touch()

            if switch_file_path.exists():

                target_media_file_path = Path(os.path.join(str(target_date_folder), media_file_path.name))
                if target_media_file_path.exists():
                    log('The file {} already exists'.format(str(target_media_file_path)))
                    continue

                log('Copying of file: ' + media_file_path_string)
                shutil.copy(media_file_path_string, str(target_date_folder))
                log(media_file_path_string + ' copied')
            else:
                log('Switch file: {} deleted for {}'.format(SWITCH_FILE_NAME, target_date_folder))


def is_video(media_file_path):
    if not os.path.isfile(media_file_path):
        return False
    file_type = get_file_type(media_file_path)
    return file_type in get_supported_video_file_types()


def is_picture(media_file):
    return os.path.isfile(media_file) and bool(imghdr.what(media_file))


if __name__ == "__main__":
    # the first argument is a script filename
    main()
