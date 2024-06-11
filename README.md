# README

The TPD-Keys repo is from [here](https://cdm-project.com/Decryption-Tools/TPD-Keys).
Comment out the line `from . import gui`.
Otherwise, it runs PySimpleGUI.
Create a virtual environment with `python3 -m venv .venv; source ./.venv/bin/activate`.
Install the dependencies with `pip3 install -r requirements.txt`
Make sure that you have a working Widevine Device (WVD) in the WVDs folder.
Now the command `python3 tpd-keys.py --udemy` is runnable.

Create a directory for curlconverter.
Run `npm init -y` and `npm install curlconverter`.
Now the command `npx curlconverter --help` is runnable

The udemy downloader repo is from [here](https://github.com/curlconverter/curlconverter).
Create a virtual environment and install the dependencies.
Add the following flag to the `yt-dlp` bash command in the `handle_segments` function for downloading segments: `-P temp:/tmp`
Otherwise, my disk goes to 100% utilization when downloading encrypted m4a files.
Replace the ffmpeg arguments `-c:v copy -c:a copy` with `-c copy -shortest` for the encrypted downloads.
Otherwise, the audio is too long.
Now the command `python3 main.py` is runnable.

Now for an Udemy course with DRM, copy the Init Data to `resources/init_data.txt` and copy the Copy as cURL to `resources/curl.txt`.

```bash
python3 -m venv .venv
source ./.venv/bin/activate
pip3 install poetry
python3 -m poetry install
python3 glue.py \
  --tpd-keys-dir $TPD_KEYS_DIR \
  --udemy-dir $UDEMY_DOWNLOADER_DIR \
  --curlconv-dir $CURL_CONVERTER_DIR
```
