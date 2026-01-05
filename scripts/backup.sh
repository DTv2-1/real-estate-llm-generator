#!/bin/bash
# =============================================================================
# BACKUP SCRIPT
# Backup PostgreSQL database and media files
# =============================================================================

set -e

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"
MEDIA_BACKUP_FILE="$BACKUP_DIR/media_backup_$DATE.tar.gz"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📦 Starting backup...${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo -e "${YELLOW}💾 Backing up database...${NC}"
docker-compose -f docker-compose.production.yml exec -T db pg_dump -U postgres -d real_estate > "$DB_BACKUP_FILE"
echo -e "${GREEN}✅ Database backed up to: $DB_BACKUP_FILE${NC}"

# Backup media files
echo -e "${YELLOW}📁 Backing up media files...${NC}"
if [ -d "media" ]; then
    tar -czf "$MEDIA_BACKUP_FILE" media/
    echo -e "${GREEN}✅ Media backed up to: $MEDIA_BACKUP_FILE${NC}"
else
    echo "⚠️  No media directory found, skipping media backup"
fi

# Delete old backups (keep last 7 days)
echo -e "${YELLOW}🧹 Cleaning old backups...${NC}"
find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "media_backup_*.tar.gz" -mtime +7 -delete

echo -e "${GREEN}✅ Backup complete!${NC}"
echo ""
echo "Backup files:"
ls -lh "$BACKUP_DIR" | tail -n 5
