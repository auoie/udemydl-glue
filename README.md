# README

## Prepare the Folders

### TPD Keys

The TPD-Keys repo is from [here](https://cdm-project.com/Decryption-Tools/TPD-Keys).

- Comment out the line `from . import gui`. Otherwise, it runs PySimpleGUI.
- Create a virtual environment with `python3 -m venv .venv; source ./.venv/bin/activate`.
- Install the dependencies with `pip3 install -r requirements.txt`
- Make sure that you have a working Widevine Device (WVD) in the WVDs folder.
- Also, the default `requests` module might not pass Cloudflare. To bypass this, install `curl_cffi` with `python3 -m pip install curl_cffi`
  and then replace `import requests` with `from curl_cffi import requests` in the file `udemy.py`.

Now the command `python3 tpd-keys.py --udemy` is runnable and will probably not fail.

### Curl Converter

Create a directory for curlconverter.
For reference, the curlconverter repo is [here](https://github.com/curlconverter/curlconverter).
Run `npm init -y` and `npm install curlconverter`.
Now the command `npx curlconverter --help` is runnable

### Udemy Downloader

The udemy downloader repo is from [here](https://github.com/auoie/udemy-dl).
Create a virtual environment and install the dependencies.
Now the command `udemy-dl` is runnable.

## Usage

Now for an Udemy course with DRM, copy the Init Data (from the browser console) to `resources/init_data.txt` and copy the Copy as cURL (filter by widevine from the Network Requests) to `resources/curl.txt`.

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
