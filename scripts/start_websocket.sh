#!/bin/bash

# Kafka configuration variables
KAFKA_COMPOSE_SERVICE="kafka1"  # Replace with your Kafka service name in Docker Compose
TOPIC_NAME="smartapi"
PARTITIONS=5
REPLICATION_FACTOR=3
KAFKA_PORT=9092

# mkdir -p ../docker/docker_data/kafka1
# mkdir -p ../docker/docker_data/kafka2
# mkdir -p ../docker/docker_data/kafka3

# sudo chown -R 1001:1001 ../docker/docker_data

# Function to check if a Docker container is running
is_container_running() {
    docker ps -f name=$1 --format '{{.Names}}' | grep -w $1 > /dev/null
}

# Function to create the topic
create_topic() {
    docker exec $KAFKA_COMPOSE_SERVICE kafka-topics.sh --create --topic $TOPIC_NAME --partitions $PARTITIONS --replication-factor $REPLICATION_FACTOR --if-not-exists --bootstrap-server $KAFKA_COMPOSE_SERVICE:$KAFKA_PORT
}

# Start Kafka container if not running
if ! is_container_running $KAFKA_COMPOSE_SERVICE; then
    echo "Starting Kafka container..."
    docker compose -f ../docker/bitnami_kafka.yaml up -d
    echo "Waiting for Kafka to start..."
    sleep 20 # Give Kafka some time to start
    create_topic
else
    echo "Kafka container is already running."
fi

# Verify topic creation
echo "Verifying if the topic '$TOPIC_NAME' exists..."
docker exec $KAFKA_COMPOSE_SERVICE kafka-topics.sh --list --bootstrap-server $KAFKA_COMPOSE_SERVICE:$KAFKA_PORT | grep -w $TOPIC_NAME && echo "Topic '$TOPIC_NAME' exists." || echo "Failed to create the topic '$TOPIC_NAME'."

conda_env_name="$(conda env list | grep "*" | awk '{print $1}')"
eval "$(conda shell.bash hook)"
conda activate "${conda_env_name}"
