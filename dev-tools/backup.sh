#!/bin/bash
# Create timestamped backup

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

cp index.html "$BACKUP_DIR/index_${TIMESTAMP}.html"
echo "✅ Backup created: $BACKUP_DIR/index_${TIMESTAMP}.html"

# Keep only last 10 backups
ls -t "$BACKUP_DIR"/index_*.html | tail -n +11 | xargs rm -f
echo "📁 Cleaned old backups (keeping 10 most recent)"
