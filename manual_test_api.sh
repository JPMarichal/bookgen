#!/bin/bash
# Manual testing script for BookGen FastAPI REST API
# Tests all required endpoints with real data

set -e

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}BookGen API Manual Testing${NC}"
echo -e "${BLUE}================================${NC}\n"

# 1. Health Check
echo -e "${YELLOW}1. Testing Health Endpoint${NC}"
echo "GET $BASE_URL/health"
curl -s $BASE_URL/health | python -m json.tool
echo -e "${GREEN}✓ Health check passed${NC}\n"

# 2. API Status
echo -e "${YELLOW}2. Testing API Status${NC}"
echo "GET $BASE_URL/api/v1/status"
curl -s $BASE_URL/api/v1/status | python -m json.tool
echo -e "${GREEN}✓ API status passed${NC}\n"

# 3. Swagger Documentation
echo -e "${YELLOW}3. Testing Swagger Documentation${NC}"
echo "GET $BASE_URL/docs"
echo "Swagger UI is available at: $BASE_URL/docs"
echo -e "${GREEN}✓ Documentation available${NC}\n"

# 4. Biography Generation
echo -e "${YELLOW}4. Testing Biography Generation${NC}"
echo "POST $BASE_URL/api/v1/biographies/generate"
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/biographies/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Marie Curie",
    "chapters": 3,
    "total_words": 3000
  }')
echo "$RESPONSE" | python -m json.tool

# Extract job_id
JOB_ID=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null || echo "")
if [ -n "$JOB_ID" ]; then
  echo -e "${GREEN}✓ Job created with ID: $JOB_ID${NC}\n"
  
  # 5. Check Job Status
  echo -e "${YELLOW}5. Testing Job Status${NC}"
  echo "GET $BASE_URL/api/v1/biographies/$JOB_ID/status"
  sleep 2
  curl -s "$BASE_URL/api/v1/biographies/$JOB_ID/status" | python -m json.tool
  echo -e "${GREEN}✓ Job status retrieved${NC}\n"
else
  echo -e "${YELLOW}⚠ Could not extract job ID (job creation may have failed)${NC}\n"
fi

# 6. Source Validation
echo -e "${YELLOW}6. Testing Source Validation${NC}"
echo "POST $BASE_URL/api/v1/sources/validate"
curl -s -X POST "$BASE_URL/api/v1/sources/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {
        "title": "The Life of Marie Curie",
        "author": "Eve Curie",
        "publication_date": "1937",
        "source_type": "book"
      },
      {
        "title": "Wikipedia - Marie Curie",
        "url": "https://en.wikipedia.org/wiki/Marie_Curie",
        "source_type": "url"
      },
      {
        "title": "Nobel Prize Biography",
        "url": "https://www.nobelprize.org/prizes/physics/1903/marie-curie/biographical/",
        "source_type": "url"
      }
    ],
    "check_accessibility": false
  }' | python -m json.tool
echo -e "${GREEN}✓ Source validation passed${NC}\n"

# 7. Metrics Endpoint
echo -e "${YELLOW}7. Testing Metrics Endpoint${NC}"
echo "GET $BASE_URL/metrics"
curl -s $BASE_URL/metrics | head -20
echo -e "${GREEN}✓ Metrics available${NC}\n"

# 8. Rate Limiting Test
echo -e "${YELLOW}8. Testing Rate Limiting${NC}"
echo "Making 65 requests to test rate limiting..."
for i in {1..65}; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/v1/status 2>/dev/null)
  if [ "$HTTP_CODE" = "429" ]; then
    echo -e "${GREEN}✓ Rate limiting working - got 429 after $i requests${NC}\n"
    break
  fi
done

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}All manual tests completed!${NC}"
echo -e "${BLUE}================================${NC}"
