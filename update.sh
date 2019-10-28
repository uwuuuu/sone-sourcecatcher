#! /bin/bash

set -e

BACKUP_DIR=backups/$(date +%s)
LIVE_DIR=live/
WORKING_DIR=working
mkdir -p $BACKUP_DIR
mkdir -p $LIVE_DIR
mkdir -p $WORKING_DIR

cp $LIVE_DIR/twitter_scraper.db $BACKUP_DIR
cp $LIVE_DIR/phash_index.ann $BACKUP_DIR
cp $LIVE_DIR/descriptors.pkl $BACKUP_DIR
cp $LIVE_DIR/BOW_annoy_map.pkl $BACKUP_DIR
cp $LIVE_DIR/kmeans.pkl $BACKUP_DIR
cp $LIVE_DIR/BOW_index.ann $BACKUP_DIR

rm -rf $WORKING_DIR/*

cp $LIVE_DIR/twitter_scraper.db $WORKING_DIR
cp $LIVE_DIR/phash_index.ann $WORKING_DIR
cp $LIVE_DIR/descriptors.pkl $WORKING_DIR
cp $LIVE_DIR/BOW_annoy_map.pkl $WORKING_DIR
cp $LIVE_DIR/kmeans.pkl $WORKING_DIR
cp $LIVE_DIR/BOW_index.ann $WORKING_DIR

source ./sourcecatcher_venv/bin/activate
python bot.py
python gen_phashes.py
python feature_match.py

cp $WORKING_DIR/twitter_scraper.db $LIVE_DIR
cp $WORKING_DIR/phash_index.ann $LIVE_DIR
cp $WORKING_DIR/descriptors.pkl $LIVE_DIR
cp $WORKING_DIR/BOW_annoy_map.pkl $LIVE_DIR
cp $WORKING_DIR/kmeans.pkl $LIVE_DIR
cp $WORKING_DIR/BOW_index.ann $LIVE_DIR

./prune_backups.sh
