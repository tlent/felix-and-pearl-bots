FROM rust:1.70 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/felix-bot /usr/local/bin/
COPY days.db /app/days.db
WORKDIR /app
# No CMD - we'll run the command directly when the container starts 