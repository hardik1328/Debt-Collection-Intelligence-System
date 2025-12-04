#!/bin/bash

# Contract Intelligence API - Test Script
# This script tests all major API endpoints

API_URL="http://localhost:8000"
SAMPLE_PDF="${1:-sample.pdf}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Contract Intelligence API - Test Suite${NC}\n"

# 1. Health Check
echo -e "${YELLOW}1. Health Check${NC}"
curl -s "$API_URL/admin/healthz" | jq .
echo

# 2. Metrics
echo -e "${YELLOW}2. Get Metrics${NC}"
curl -s "$API_URL/admin/metrics" | jq .
echo

# 3. Upload Document
echo -e "${YELLOW}3. Upload PDF Document${NC}"
if [ -f "$SAMPLE_PDF" ]; then
    INGEST_RESPONSE=$(curl -s -X POST "$API_URL/ingest" \
      -F "files=@$SAMPLE_PDF")
    echo "$INGEST_RESPONSE" | jq .
    
    # Extract document ID
    DOC_ID=$(echo "$INGEST_RESPONSE" | jq -r '.document_ids[0]')
    echo -e "${GREEN}Document ID: $DOC_ID${NC}\n"
    
    # 4. List Documents
    echo -e "${YELLOW}4. List Documents${NC}"
    curl -s "$API_URL/ingest/documents" | jq .
    echo
    
    # 5. Extract Fields
    echo -e "${YELLOW}5. Extract Contract Fields${NC}"
    curl -s -X POST "$API_URL/extract?document_id=$DOC_ID" | jq .
    echo
    
    # 6. Ask Question
    echo -e "${YELLOW}6. Ask Question${NC}"
    curl -s -X POST "$API_URL/ask" \
      -H "Content-Type: application/json" \
      -d "{\"question\":\"What are the payment terms?\",\"document_ids\":[\"$DOC_ID\"]}" | jq .
    echo
    
    # 7. Run Audit
    echo -e "${YELLOW}7. Run Risk Audit${NC}"
    curl -s -X POST "$API_URL/audit?document_id=$DOC_ID" | jq .
    echo
    
    # 8. Get Audit Summary
    echo -e "${YELLOW}8. Get Audit Summary${NC}"
    curl -s "$API_URL/audit/summary/$DOC_ID" | jq .
    echo
    
else
    echo -e "${RED}Error: Sample PDF not found at $SAMPLE_PDF${NC}"
fi

echo -e "${GREEN}Test suite completed!${NC}"
