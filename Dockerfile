# Builder stage
FROM rust:slim AS builder

WORKDIR /app

# Copy only files needed for dependency resolution
COPY Cargo.toml Cargo.lock ./

# Create a dummy main.rs to build dependencies
RUN mkdir -p src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Now copy the real source code
COPY . .

# Build the actual application
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Copy only the built binary
COPY --from=builder /app/target/release/felix-bot /usr/local/bin/

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the application
RUN groupadd -r felix && useradd -r -g felix felix

WORKDIR /app

# Create a directory for the database and set permissions
RUN mkdir -p /app && chown -R felix:felix /app

# Switch to non-root user
USER felix

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/felix-bot"] 