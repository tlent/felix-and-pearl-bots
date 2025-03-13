# Builder stage
FROM rust:slim AS builder

WORKDIR /app

# Copy the entire project
COPY . .

# Build the application with optimizations
RUN cargo build --release

# Runtime stage - using a much smaller base image
FROM debian:bookworm-slim AS runtime

# Copy only the built binary
COPY --from=builder /app/target/release/felix-bot /usr/local/bin/

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean autoclean && \
    apt-get autoremove --yes

# Create a non-root user to run the application
RUN groupadd -r felix && useradd -r -g felix felix

WORKDIR /app

# Set permissions
RUN chown -R felix:felix /app

# Switch to non-root user
USER felix

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/felix-bot"] 