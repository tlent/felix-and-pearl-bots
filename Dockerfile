# Builder stage: Compile the Rust application for ARM64
FROM rust:slim AS builder

WORKDIR /app

# Install minimal build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pkg-config \
    libsqlite3-dev \
    gcc-aarch64-linux-gnu \
    libc6-dev-arm64-cross \
    && rm -rf /var/lib/apt/lists/*

# Set up Rust toolchain for ARM64
RUN rustup target add aarch64-unknown-linux-gnu

# Configure Cargo for cross-compilation
RUN mkdir -p .cargo && \
    echo '[target.aarch64-unknown-linux-gnu]' > .cargo/config.toml && \
    echo 'linker = "aarch64-linux-gnu-gcc"' >> .cargo/config.toml

# Copy dependency files first for caching
COPY Cargo.toml Cargo.lock ./
COPY .cargo .cargo/

# Create a dummy main.rs to build dependencies
RUN mkdir -p src && \
    echo 'fn main() { println!("Dummy build"); }' > src/main.rs

# Build and cache dependencies
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    cargo build --target aarch64-unknown-linux-gnu --release

# Copy the actual source code
COPY src src/

# Build the application and strip the binary
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/app/target \
    touch src/main.rs && \
    cargo build --target aarch64-unknown-linux-gnu --release && \
    cp target/aarch64-unknown-linux-gnu/release/felix-bot /app/felix-bot && \
    aarch64-linux-gnu-strip /app/felix-bot

# Runtime stage: Create a minimal image
FROM debian:bookworm-slim AS runtime

# Install runtime dependencies (remove ca-certificates if not needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r felix && useradd -r -g felix felix

# Set up working directory and permissions
WORKDIR /app
RUN chown -R felix:felix /app

# Copy the binary from the builder stage
COPY --from=builder /app/felix-bot /usr/local/bin/
RUN chmod 755 /usr/local/bin/felix-bot

# Switch to non-root user
USER felix

# Define the entrypoint
ENTRYPOINT ["/usr/local/bin/felix-bot"]