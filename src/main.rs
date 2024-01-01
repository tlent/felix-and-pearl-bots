use regex::Regex;
use serenity::async_trait;
use serenity::model::channel::Message;
use serenity::model::prelude::Ready;
use serenity::prelude::*;
use std::env;
use std::sync::OnceLock;

struct Handler;

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

#[tokio::main]
async fn main() {
    let token = env::var("DISCORD_TOKEN").expect("Missing DISCORD_TOKEN environment variable");
    let intents = GatewayIntents::GUILD_MESSAGES | GatewayIntents::MESSAGE_CONTENT;
    let mut client = Client::builder(&token, intents)
        .event_handler(Handler)
        .await
        .expect("Error creating client");
    if let Err(err) = client.start().await {
        eprintln!("Client error: {err:?}");
    }
}
