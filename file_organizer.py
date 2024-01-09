# Import necessary libraries
import os
import shutil
import logging
from PIL import Image, ExifTags
from datetime import datetime
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import hashlib

# Set up logging
logging.basicConfig(filename='file_organizer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

# Function to get creation date of a video file
def get_video_date_taken(path):
    try:
        parser = createParser(path)
        if not parser:
            logger.error(f"Unable to parse video {path}")
            return None
        with parser:
            metadata = extractMetadata(parser)
        if not metadata:
            logger.error(f"Unable to extract metadata from video {path}")
            return None
        return metadata.get('creation_date')
    except Exception as e:
        logger.error(f"Error reading creation date from video {path}: {e}")
        return None

# Function to get creation date of a file
def get_date_taken(path):
    try:
        # If file is a video file
        if path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            date_taken = get_video_date_taken(path)
            if date_taken is not None:
                return date_taken.strftime('%Y:%m:%d %H:%M:%S')
            else:
                timestamp = os.path.getmtime(path)
        else:
            # If file is an image file
            if os.path.getsize(path) > 89478485:
                logger.warning(f"Skipping large image {path}")
                timestamp = os.path.getmtime(path)
            else:
                image = Image.open(path)
                if hasattr(image, '_getexif'):
                    exif_data = image._getexif()
                    if exif_data is not None:
                        for tag, value in exif_data.items():
                            if ExifTags.TAGS.get(tag) == 'DateTimeOriginal':
                                return value
                timestamp = os.path.getmtime(path)
    except (KeyError, TypeError, AttributeError, IOError) as e:
        logger.error(f"Error reading EXIF data from {path}: {e}")
        timestamp = os.path.getmtime(path)

    return datetime.fromtimestamp(timestamp).strftime('%Y:%m:%d %H:%M:%S')

# Function to get hash of a file
def get_file_hash(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Function to compare two files
def compare_files(file1, file2):
    return os.path.getsize(file1) == os.path.getsize(file2) and get_file_hash(file1) == get_file_hash(file2)

# Function to process a file
def process_file(filename, dirpath, file_types, dest_folder, move_files, delete_files, dry_run, year_only, day_only, month_only, rename_files, skip_existing, maintain_metadata, organize_by_type, ignore_types, organize_by_size, organize_by_name, eliminate_duplicates):
    result = {"moved": 0, "copied": 0, "renamed": 0, "deleted": 0}

    # If file is of the specified types and not of the ignored types
    if filename.lower().endswith(tuple(file_types)) and not filename.lower().endswith(tuple(ignore_types)):
        full_path = os.path.join(dirpath, filename)
        date_taken = get_date_taken(full_path)
        try:
            year, month, day_time = date_taken.split(':', 2)
            day, time = day_time.split(' ')
            time = time.replace(':', '_')
            month_name = datetime(year=int(year), month=int(month), day=int(day)).strftime('%B')
        except ValueError as e:
            logger.error(f"Invalid date format in {full_path}: {e}")
            return result

        # Rename file if rename_files is True
        new_filename = f"{day}_{month_name}_{time}{os.path.splitext(filename)[1]}" if rename_files else filename
        year_folder = os.path.join(dest_folder, year)
        month_folder = os.path.join(year_folder, f"{month}.{month_name}") if not year_only else year_folder
        day_folder = os.path.join(month_folder, day) if day_only else month_folder
        final_folder = os.path.join(day_folder, os.path.splitext(filename)[1][1:]) if organize_by_type else day_folder

        if month_only:
            final_folder = month_folder

        # Organize by size if organize_by_size is True
        if organize_by_size:
            size = os.path.getsize(full_path)
            if size < 1024 * 1024:
                final_folder = os.path.join(final_folder, 'Small')
            elif size < 1024 * 1024 * 1024:
                final_folder = os.path.join(final_folder, 'Medium')
            else:
                final_folder = os.path.join(final_folder, 'Large')

        # Organize by name if organize_by_name is True
        if organize_by_name:
            initial = filename[0].upper()
            final_folder = os.path.join(final_folder, initial)

        if dry_run:
            logger.info(f"Would create folder {final_folder}")
        else:
            try:
                os.makedirs(final_folder, exist_ok=True)
            except PermissionError as e:
                logger.error(f"Permission denied: {e}")
                return result

        # Skip duplicate files if eliminate_duplicates is True
        if eliminate_duplicates:
            for root, dirs, files in os.walk(dest_folder):
                for file in files:
                    if compare_files(os.path.join(root, file), full_path):
                        logger.info(f"Duplicate file {full_path} skipped")
                        return result

        # Skip existing files if skip_existing is True
        if os.path.exists(os.path.join(final_folder, new_filename)):
            if skip_existing:
                logger.info(f"Skipping existing file {os.path.join(final_folder, new_filename)}")
                return result
            i = 1
            while os.path.exists(os.path.join(final_folder, f"{new_filename.split('.')[0]}({i}).{new_filename.split('.')[1]}")):
                i += 1
            new_filename = f"{new_filename.split('.')[0]}({i}).{new_filename.split('.')[1]}"

        # Move files if move_files is True
        if move_files:
            if dry_run:
                logger.info(f"Would move {full_path} to {os.path.join(final_folder, new_filename)}")
            else:
                try:
                    shutil.move(full_path, os.path.join(final_folder, new_filename))
                    logger.info(f"Moved {full_path} to {os.path.join(final_folder, new_filename)}")
                    result["moved"] += 1
                    if rename_files:
                        result["renamed"] += 1
                except Exception as e:
                    logger.error(f"Error moving {full_path} to {os.path.join(final_folder, new_filename)}: {e}")
        else:
            # Copy files if move_files is False
            if dry_run:
                logger.info(f"Would copy {full_path} to {os.path.join(final_folder, new_filename)}")
            else:
                try:
                    shutil.copy2(full_path, os.path.join(final_folder, new_filename))
                    if maintain_metadata:
                        shutil.copystat(full_path, os.path.join(final_folder, new_filename))
                    logger.info(f"Copied {full_path} to {os.path.join(final_folder, new_filename)}")
                    result["copied"] += 1
                    if rename_files:
                        result["renamed"] += 1
                except Exception as e:
                    logger.error(f"Error copying {full_path} to {os.path.join(final_folder, new_filename)}: {e}")

        # Delete files if delete_files is True and move_files is False
        if delete_files and not move_files:
            if dry_run:
                logger.info(f"Would delete {full_path}")
            else:
                try:
                    os.remove(full_path)
                    logger.info(f"Deleted {full_path}")
                    result["deleted"] += 1
                except Exception as e:
                    logger.error(f"Error deleting {full_path}: {e}")

    return result

# Function to organize files by date
def organize_files_by_date(source_folder, dest_folder, move_files=True, delete_files=False, dry_run=False, year_only=False, day_only=False, month_only=False, rename_files=False, skip_existing=False, maintain_metadata=False, organize_by_type=False, ignore_types=[], organize_by_size=False, organize_by_name=False, eliminate_duplicates=False, progress_callback=None):
    if source_folder == dest_folder:
        logger.error("Source and destination folders cannot be the same.")
        return

    # Define file types
    file_types = ['.jpg', '.png', '.jpeg', '.mp4', '.avi', '.mov', '.mkv', '.dng', '.gif', '.bmp', '.heic', '.tiff', '.webp', '.raw', '.indd', '.ai', '.eps', '.pdf', '.svg', '.psd', '.flv', '.m2ts', '.mts', '.ts', '.m4v', '.wmv', '.ogv', '.3gp', '.3g2', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.csv', '.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma']
    total_files = sum([len(files) for r, d, files in os.walk(source_folder)])
    progress_bar = tqdm(total=total_files, ncols=70)

    result = {"moved": 0, "copied": 0, "renamed": 0, "deleted": 0}

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = []
        for dirpath, dirnames, filenames in os.walk(source_folder):
            for filename in filenames:
                futures.append(executor.submit(process_file, filename, dirpath, file_types, dest_folder, move_files, delete_files, dry_run, year_only, day_only, month_only, rename_files, skip_existing, maintain_metadata, organize_by_type, ignore_types, organize_by_size, organize_by_name, eliminate_duplicates))

        for future in concurrent.futures.as_completed(futures):
            file_result = future.result()
            progress_bar.update()
            for key in result:
                result[key] += file_result[key]

            if progress_callback is not None:
                progress_callback()

    progress_bar.close()

    return result
