![Repo Icon](./icon.png)

# Pix-Jinx: Make Sense of Your Media Mess

Welcome to Pix-Jinx, your new best friend in managing and organizing your ever-growing collection of images and videos. This nifty tool, built with Python and PyQt5, is designed to help you bring order to your media chaos. It's powerful, flexible, and user-friendly, making it a breeze to use whether you're a tech newbie or a seasoned pro.

## What Can Pix-Jinx Do?

- **Date-Based Organization**: Pix-Jinx can sort your files based on the date they were created. You can even break it down by year, month, or day.
- **Type-Based Organization**: Want to keep your JPEGs separate from your PNGs? Pix-Jinx has got you covered.
- **Size-Based Organization**: Pix-Jinx can group your files into Small, Medium, and Large categories based on their sizes.
- **Name-Based Organization**: If you're a fan of the alphabet, you can have your files organized from A to Z.
- **Duplicate Detection**: Pix-Jinx can spot and eliminate duplicate files, freeing up precious storage space.
- **File Renaming**: Pix-Jinx can rename your files following a consistent format for easier identification.
- **Dry Run**: Not sure about the changes? Perform a dry run to see the proposed organization without actually moving or renaming files.
- **Progress Tracking**: Keep an eye on the progress bar and detailed logs to track the organization process.

## Getting Started

Before you start, make sure you have Python 3.6 or later installed on your system. If you don't, head over to the [official Python website](https://www.python.org/downloads/) and download the latest version.

### Step 1: Set Up a Virtual Environment

It's a good practice to create a virtual environment for each Python project to keep dependencies isolated. Here's how you can set it up:

1. Open a terminal and navigate to the directory where you want to set up the project.
2. Run the following command to create a new virtual environment:

```bash
python3 -m venv pixjinx-env
```

3. Activate the virtual environment:

- On macOS and Linux:

```bash
source pixjinx-env/bin/activate
```

- On Windows:

```bash
.\pixjinx-env\Scripts\activate
```

### Step 2: Install Dependencies

With your virtual environment activated, install the necessary dependencies by running:

```bash
pip install -r requirements.txt
```

### Step 3: Run Pix-Jinx

Now you're all set to run Pix-Jinx and start organizing!

## How to Use Pix-Jinx

1. **Select Source Folder**: Click on the "Select Source Folder" button and choose the folder that contains the files you want to organize.
2. **Select Destination Folder**: Click on the "Select Destination Folder" button and choose where you want the organized files to end up.
3. **Choose Your Options**: Pick the options that work best for you. You can choose to move or copy files, delete files after copying, and whether to perform a dry run. You can also choose to organize by year only, day only, month only, by type, by size, or by name. If you want to ignore certain file types, just pop them in the "Ignore types" field.
4. **Hit Organize**: Click on the "Organize" button to start the organization process. Keep an eye on the progress bar and check the detailed logs for more info.
5. **Check Out the Results**: Once Pix-Jinx has done its magic, head over to the destination folder and the logs to review the results.

## Contributing

Got an idea to make Pix-Jinx even better? I'd love to hear it! Feel free to submit a Pull Request or open an Issue.

## License

Pix-Jinx is a free public tool, released under the MIT License.
