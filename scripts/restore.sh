#!/bin/bash
# =============================================================================
# RESTORE SCRIPT
# Restore PostgreSQL database and media files from backup
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Backup date required${NC}"
    echo "Usage: ./restore.sh YYYYMMDD_HHMMSS"
    echo ""
    echo "Available backups:"
    ls -1 backups/db_backup_*.sql 2>/dev/null | sed 's/backups\/db_backup_/  /' | sed 's/.sql//' || echo "  No backups found"
    exit 1
fi

BACKUP_DATE=$1
BACKUP_DIR="./backups"
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$BACKUP_DATE.sql"
MEDIA_BACKUP_FILE="$BACKUP_DIR/media_backup_$BACKUP_DATE.tar.gz"

# Check if backup exists
if [ ! -f "$DB_BACKUP_FILE" ]; then
    echo -e "${RED}❌ Error: Backup file not found: $DB_BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will overwrite the current database!${NC}"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Restore database
echo -e "${YELLOW}💾 Restoring database...${NC}"
docker-compose -f docker-compose.production.yml exec -T db psql -U postgres -d real_estate < "$DB_BACKUP_FILE"
echo -e "${GREEN}✅ Database restored!${NC}"

# Restore media files
if [ -f "$MEDIA_BACKUP_FILE" ]; then
    echo -e "${YELLOW}📁 Restoring media files...${NC}"
    tar -xzf "$MEDIA_BACKUP_FILE"
    echo -e "${GREEN}✅ Media restored!${NC}"
else
    echo "⚠️  No media backup found, skipping media restore"
fi

echo -e "${GREEN}✅ Restore complete!${NC}"
