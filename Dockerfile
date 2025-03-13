# Builder stage
FROM rust:slim AS builder

WORKDIR /app

# Install build dependencies including SQLite development libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pkg-config \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the files needed for dependency resolution first
COPY Cargo.toml Cargo.lock ./

# Create a minimal src directory with a dummy main
RUN mkdir -p src && \
    echo 'fn main() {}' > src/main.rs

# Build dependencies only - this layer will be cached unless Cargo.toml/Cargo.lock change
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    cargo build --release

# Now copy the actual source code
COPY src src/

# Build the application with optimizations and copy the binary to a known location
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    touch src/main.rs && \
    cargo build --release && \
    cp target/release/felix-bot /app/felix-bot && \
    strip /app/felix-bot

# Runtime stage - using a much smaller base image
FROM debian:bookworm-slim AS runtime

# Install only essential runtime dependencies including SQLite in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean autoclean && \
    apt-get autoremove --yes

# Create a non-root user to run the application
RUN groupadd -r felix && useradd -r -g felix felix

# Create directory structure and set permissions
WORKDIR /app
RUN chown -R felix:felix /app

# Copy only the built binary - do this after setting up the environment
COPY --from=builder /app/felix-bot /usr/local/bin/

# Set proper permissions for the binary
RUN chmod 755 /usr/local/bin/felix-bot

# Switch to non-root user
USER felix

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/felix-bot"] 