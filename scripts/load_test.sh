#!/bin/sh

# Define the base URL and parameters
BASE_URL="http://localhost:8000/"
REQUESTS=100000  # Set your desired number of requests
CONC=1000      # Set your desired concurrency level

# List of URLs to test
URLS=(
  "employees/employees/"
  "products/products/"
  "orders/orders/"
)


# Loop through the URLs and run ab for each in the background
for ((i=0; i<${#URLS[@]}; i++)); do
  URL="${URLS[i]}"
  LOG_FILE="test_${i}_ab.log"  # Use index in the log file name

  # Construct the full URL for the current iteration
  FULL_URL="${BASE_URL}/${URL}"

  # Run ab in the background for the current URL
  ab -n $REQUESTS -c $CONC -k "$FULL_URL" > "$LOG_FILE" 2>&1 &

  echo "Testing URL ${i}: $FULL_URL"
  echo "Log file: $LOG_FILE"
done

# Wait for all background processes to finish
wait

echo "All tests have finished."
