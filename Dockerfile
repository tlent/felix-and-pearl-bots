# Builder stage
FROM rust:slim AS builder

WORKDIR /app

# Install build dependencies including SQLite development libraries and cross
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pkg-config \
    libsqlite3-dev \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    libc6-dev-arm64-cross \
    && rm -rf /var/lib/apt/lists/*

# Install cargo-cross with caching
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    cargo install cross

# Copy only the files needed for dependency resolution first
COPY Cargo.toml Cargo.lock ./
COPY .cargo .cargo/
COPY Cross.toml ./

# Create a minimal src directory with a dummy main
RUN mkdir -p src && \
    echo 'fn main() { println!("Dummy build for caching dependencies"); }' > src/main.rs

# Build dependencies only - this layer will be cached unless Cargo.toml/Cargo.lock change
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/app/target \
    cross build --target aarch64-unknown-linux-gnu --release

# Now copy the actual source code
COPY src src/

# Build the application with cross for ARM64
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/app/target \
    touch src/main.rs && \
    cross build --target aarch64-unknown-linux-gnu --release && \
    cp target/aarch64-unknown-linux-gnu/release/felix-bot /app/felix-bot && \
    aarch64-linux-gnu-strip /app/felix-bot

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