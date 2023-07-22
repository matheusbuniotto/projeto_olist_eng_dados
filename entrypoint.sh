#!/bin/bash

# Start the MySQL service
/usr/local/bin/docker-entrypoint.sh mysqlW &

# Run the `docker exec` command
docker exec -u 0 -it CONTAINER_ID bin/bash

# Keep the container running
tail -f /dev/null
