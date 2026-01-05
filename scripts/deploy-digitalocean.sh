#!/bin/bash
# =============================================================================
# DIGITAL OCEAN APP PLATFORM DEPLOYMENT
# Deploy Django app to Digital Ocean App Platform using doctl CLI
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🌊 Digital Ocean App Platform Deployment${NC}"
echo ""

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${YELLOW}📦 Installing doctl CLI...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install doctl
        else
            echo -e "${RED}❌ Homebrew not found. Install from: https://docs.digitalocean.com/reference/doctl/how-to/install/${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        cd ~
        wget https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz
        tar xf ~/doctl-1.94.0-linux-amd64.tar.gz
        sudo mv ~/doctl /usr/local/bin
    else
        echo -e "${RED}❌ Unsupported OS. Install doctl from: https://docs.digitalocean.com/reference/doctl/how-to/install/${NC}"
        exit 1
    fi
fi

# Check if authenticated
echo -e "${YELLOW}🔐 Checking Digital Ocean authentication...${NC}"
if ! doctl auth list &> /dev/null; then
    echo -e "${YELLOW}Please enter your Digital Ocean API token:${NC}"
    read -s DO_TOKEN
    doctl auth init -t "$DO_TOKEN"
fi

# Verify authentication
if ! doctl account get &> /dev/null; then
    echo -e "${RED}❌ Authentication failed. Please check your token.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Authenticated!${NC}"
echo ""

# Check if app exists
APP_ID="8aa471db-b3dd-40f0-9bfe-731dc1c515bd"

if doctl apps get "$APP_ID" &> /dev/null; then
    echo -e "${YELLOW}📱 Updating existing app: $APP_ID${NC}"
    
    # Update app spec
    doctl apps update "$APP_ID" --spec .do/app.yaml
    
    echo -e "${GREEN}✅ App configuration updated!${NC}"
    echo ""
    echo "Creating new deployment..."
    
    # Trigger deployment
    doctl apps create-deployment "$APP_ID" --wait
    
    echo -e "${GREEN}🎉 Deployment complete!${NC}"
    
else
    echo -e "${YELLOW}🆕 Creating new app...${NC}"
    
    # Create new app
    doctl apps create --spec .do/app.yaml
    
    echo -e "${GREEN}✅ App created!${NC}"
fi

echo ""
echo -e "${GREEN}📊 App Status:${NC}"
doctl apps get "$APP_ID"

echo ""
echo -e "${GREEN}🌐 Access your app at:${NC}"
APP_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)
echo "$APP_URL"

echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Set environment variables in Digital Ocean dashboard"
echo "2. Configure custom domain (optional)"
echo "3. Monitor logs: doctl apps logs $APP_ID --type run"
echo "4. Check deployment: doctl apps list-deployments $APP_ID"
