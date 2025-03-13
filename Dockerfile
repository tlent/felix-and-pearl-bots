# Builder stage
FROM rust:slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a new empty shell project for dependency caching
WORKDIR /app
COPY Cargo.toml Cargo.lock ./

# Build only the dependencies to cache them
RUN mkdir -p src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Now build the actual application
COPY . .
RUN cargo build --release

# Runtime stage - use a smaller base image
FROM debian:bullseye-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /app/target/release/felix-bot /usr/local/bin/felix-bot

# Create a directory for the database
RUN mkdir -p /app

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/felix-bot"] 