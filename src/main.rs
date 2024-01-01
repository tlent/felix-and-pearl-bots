use regex::Regex;
use serenity::all::ChannelId;
use serenity::async_trait;
use serenity::http::Http;
use serenity::model::channel::Message;
use serenity::model::prelude::Ready;
use serenity::prelude::*;
use std::env;
use std::sync::{Arc, OnceLock};
use time::macros::time;

struct Handler;

#[tokio::main]
async fn main() {
    let token = env::var("DISCORD_TOKEN").expect("Missing DISCORD_TOKEN environment variable");
    let intents = GatewayIntents::GUILD_MESSAGES | GatewayIntents::MESSAGE_CONTENT;
    let mut client = Client::builder(&token, intents)
        .event_handler(Handler)
        .await
        .expect("Error creating client");
    tokio::spawn(national_day_interval(client.http.clone()));
    if let Err(err) = client.start().await {
        eprintln!("Client error: {err:?}");
    }
}

#[async_trait]
impl EventHandler for Handler {
    async fn message(&self, context: Context, message: Message) {
        static REGEX: OnceLock<Regex> = OnceLock::new();
        let regex = REGEX.get_or_init(|| {
            Regex::new(r"\b(https?://(?:www\.)?)(?:twitter\.com|x\.com)(/\S*)").unwrap()
        });
        let new_host = "fixupx.com";
        let mut reply = String::new();
        for captures in regex.captures_iter(&message.content) {
            let (_, [before, after]) = captures.extract();
            reply.reserve(before.len() + new_host.len() + after.len() + 1);
            reply.push_str(before);
            reply.push_str(new_host);
            reply.push_str(after);
            reply.push('\n');
        }
        if reply.is_empty() {
            return;
        }
        if let Err(err) = message.channel_id.say(&context.http, reply).await {
            eprintln!("Error sending message: {err:?}");
        }
    }

    async fn ready(&self, _: Context, ready: Ready) {
        println!("{} is connected", ready.user.name);
    }
}

async fn national_day_interval(http: Arc<Http>) {
    let now = time::OffsetDateTime::now_local().unwrap();
    let mut start = now;
    if start.time() >= time!(7:00) {
        start += time::Duration::days(1);
    }
    start = start.replace_time(time!(7:00));
    let duration_to_start = start - now;
    let duration_to_start = std::time::Duration::new(
        duration_to_start.whole_seconds() as u64,
        duration_to_start.subsec_nanoseconds() as u32,
    );
    let start = tokio::time::Instant::now() + duration_to_start;
    let mut interval =
        tokio::time::interval_at(start, std::time::Duration::from_secs(24 * 60 * 60));
    loop {
        interval.tick().await;
        if let Err(err) = ChannelId::new(1191225413758894130)
            .say(&http, "national days")
            .await
        {
            eprintln!("Error saying national days: {err:?}");
        }
    }
}
