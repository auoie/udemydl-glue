#!/bin/sh

COURSE_NAME="$1"
COURSE_URL="$2"
INSTRUCTOR_NAME="$3"
DOWNLOADER_PATH="$4"
KEY_PAIR_JSON="$(cat)"

cd "$DOWNLOADER_PATH" || exit

ACTIVATE_FILE="$DOWNLOADER_PATH/.venv/bin/activate"
KEYFILE_PATH="$DOWNLOADER_PATH/keyfile.json"
KEYS_DIR="$DOWNLOADER_PATH/keys"
COURSE_KEY_FILE="$KEYS_DIR/$COURSE_NAME.json"
OUTPUT_DIR="$DOWNLOADER_PATH/glue_dir/$INSTRUCTOR_NAME"

echo "$COURSE_NAME"
echo "$COURSE_URL"
echo "$INSTRUCTOR_NAME"
echo "$KEY_PAIR_JSON"
echo "$DOWNLOADER_PATH"
echo "$ACTIVATE_FILE"
echo "$KEYFILE_PATH"
echo "$COURSE_KEY_FILE"
echo "$OUTPUT_DIR"

. "$ACTIVATE_FILE"
mkdir -p "$KEYS_DIR"
touch "$COURSE_KEY_FILE"
echo "$KEY_PAIR_JSON" > "$COURSE_KEY_FILE"
rm "$KEYFILE_PATH"
ln -s "$COURSE_KEY_FILE" "$KEYFILE_PATH"

udemy-dl \
  --batch-playlists \
  --embed-subs \
  --decrypt \
  --concurrent-downloads 30 \
  --save-to-file \
  --browser firefox \
  --course "$COURSE_URL" \
  --out out_dir
