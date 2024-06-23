import argparse
import os
from pathlib import Path
import subprocess
import json
import base64
import sys
from dataclasses import dataclass
from urllib import parse
from bs4 import BeautifulSoup, Tag
import requests
from generated import curl_json


def get_pssh(init_data: str) -> str:
    delimiter = "70737368"
    hex_value = base64.b64decode(init_data).hex()
    index = hex_value.rfind(delimiter)
    ending = hex_value[index - 8 :]
    result = base64.b64encode(bytes.fromhex(ending)).decode()
    return result


@dataclass
class KeyPairReferer:
    key_pair_json: str
    referer_url: str


def get_tpd_keys(curl_converter_dir: Path, tpd_keys_dir: Path):
    scripting_dir = Path.joinpath(Path.cwd()).resolve()
    curl_txt_path = Path.joinpath(scripting_dir, "resources", "curl.txt").resolve()
    init_data_txt_path = Path.joinpath(
        scripting_dir, "resources", "init_data.txt"
    ).resolve()
    license_curl_path = Path.joinpath(tpd_keys_dir, "license_curl.py").resolve()
    os.chdir(curl_converter_dir)
    curl_command = curl_txt_path.read_text()
    args = ["npx", "curlconverter", "--language", "python", "-"]
    try:
        process = subprocess.run(
            args,
            check=True,
            text=True,
            shell=False,
            input=curl_command,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print("ERROR:", e, e.stderr, sep="\n")
        sys.exit(1)
    curl_python_output_str = process.stdout
    chunks = [chunk.strip() for chunk in curl_python_output_str.strip().split("\n\n")]
    first_word_to_chunk: dict[str, str] = {}
    for chunk in chunks:
        first_word = chunk.split(maxsplit=1)[0]
        first_word_to_chunk[first_word] = chunk
    python_cookies = first_word_to_chunk["cookies"]
    python_headers = first_word_to_chunk["headers"]
    license_curl_path.write_text("".join([python_headers, "\n", python_cookies, "\n"]))
    args = ["npx", "curlconverter", "--language", "json", "-"]
    try:
        process = subprocess.run(
            args,
            check=True,
            text=True,
            shell=False,
            input=curl_command,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print("ERROR:", e, e.stderr, sep="\n")
        sys.exit(1)
    curl_json_output_str = process.stdout
    curl_json_output = curl_json.Model.model_validate_json(curl_json_output_str)
    raw_url = curl_json_output.raw_url
    print("RAW URL:", raw_url, "\n", sep="\n")
    referer_url = curl_json_output.headers.Referer
    print("REFERER URL:", referer_url, "\n", sep="\n")
    init_data_str = init_data_txt_path.read_text().strip()
    pssh_value = get_pssh(init_data_str)
    os.chdir(scripting_dir)
    args = ["/bin/sh", "./get-tpd.sh", str(tpd_keys_dir)]
    try:
        process = subprocess.run(
            args,
            check=True,
            text=True,
            shell=False,
            input=(pssh_value + "\n" + raw_url),
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print("ERROR:", e, e.stderr, sep="\n")
        sys.exit(1)

    command_output = process.stdout.strip()
    print(
        "GET-TPD OUTPUT (max 1000 characters):",
        command_output[: min(1000, len(command_output))],
        "\n",
        sep="\n",
    )
    key_pair = command_output.split("\n")[-1].split(":")
    if (not key_pair[0].isalnum()) or (not key_pair[1].isalnum()):
        print("EXITING: key pair is invalid")
        sys.exit(1)
    key_pair_dict = {key_pair[0]: key_pair[1]}
    key_pair_json = json.dumps(key_pair_dict, indent=4)
    print("JSON KEY PAIR:", key_pair_json, "\n", sep="\n")
    return KeyPairReferer(key_pair_json, referer_url)


def get_course_name(referer_url: str) -> str:
    parsed_url = parse.urlparse(referer_url)
    url_path_arr = parsed_url.path.split("/")
    return url_path_arr[2]


@dataclass
class CourseData:
    course_name: str
    course_url: str


def get_course_data(referer_url: str) -> CourseData:
    parsed_url = parse.urlparse(referer_url)
    url_path_arr = parsed_url.path.split("/")
    course_name = url_path_arr[2]
    new_path = "".join(["/course/", course_name, "/"])
    course_url = "".join(["https://", parsed_url.netloc, new_path])
    return CourseData(course_name, course_url)


def fetch_instructor_name(course_url: str) -> str | None:
    response = requests.get(course_url)
    body = response.text
    soup = BeautifulSoup(body, "html.parser")
    head = soup.head
    if head is None:
        return None
    instructors = head.find_all("meta", attrs={"property": "udemy_com:instructor"})
    if len(instructors) == 0:
        return None
    instructor_tag: Tag = instructors[0]
    instructor_url: str | None = instructor_tag.attrs["content"]
    if instructor_url is None:
        return None
    parsed_instuctor_url = parse.urlparse(instructor_url)
    return parsed_instuctor_url.path.split("/")[2]


@dataclass
class Arguments:
    tpd_keys_dir: Path
    curl_conv_dir: Path
    udemy_dir: Path


def parse_arguments():
    parser = argparse.ArgumentParser(description="Specify folder locations")
    parser.add_argument(
        "--tpd-keys-dir", required=True, help="Path to TPD keys directory"
    )
    parser.add_argument(
        "--udemy-dir", required=True, help="Path to udemy downloader directory"
    )
    parser.add_argument(
        "--curlconv-dir", required=True, help="Path to curl converter directory"
    )
    args = parser.parse_args()
    return Arguments(
        curl_conv_dir=Path(args.curlconv_dir).resolve(),
        tpd_keys_dir=Path(args.tpd_keys_dir).resolve(),
        udemy_dir=Path(args.udemy_dir).resolve(),
    )


def run_udemy_downloader(
    course_name: str,
    course_learn_url: str,
    instructor_name: str,
    key_pair_json: str,
    udemy_downloader_dir: Path,
):
    print("PREPARING AND RUNNING UDEMY DOWNLOADER:")
    scripting_dir = Path.joinpath(Path.cwd()).resolve()
    os.chdir(scripting_dir)
    args = [
        "/bin/sh",
        "./run-udemy-downloader.sh",
        course_name,
        course_learn_url,
        instructor_name,
        str(udemy_downloader_dir),
    ]
    try:
        process = subprocess.run(
            args,
            check=True,
            text=True,
            shell=False,
            input=key_pair_json,
            stderr=sys.stdout,
            stdout=sys.stdout,
        )
    except subprocess.CalledProcessError as e:
        print("ERROR:", e, e.stderr, sep="\n")
        sys.exit(1)
    print("Done. Status code:", process.returncode)


if __name__ == "__main__":
    args = parse_arguments()
    print(args)
    tpd_output = get_tpd_keys(
        curl_converter_dir=args.curl_conv_dir, tpd_keys_dir=args.tpd_keys_dir
    )
    course_data = get_course_data(tpd_output.referer_url)
    instructor_name = fetch_instructor_name(course_data.course_url)
    if instructor_name is None:
        print("INSTRUCTOR NOT FOUND")
        sys.exit(1)
    print("COURSE_DATA:", course_data)
    print("INSTRUCTOR_NAME:", instructor_name + "\n\n")
    run_udemy_downloader(
        course_data.course_name,
        course_data.course_url + "learn",
        instructor_name,
        tpd_output.key_pair_json,
        udemy_downloader_dir=args.udemy_dir,
    )
