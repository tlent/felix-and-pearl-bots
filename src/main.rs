use rusqlite::OptionalExtension;
use serenity::all::ChannelId;
use serenity::prelude::*;
use std::env;
use time::macros::format_description;
use time::OffsetDateTime;

const DB_PATH: &str = "days.db";
const CHANNEL_ID: u64 = 1108866354980855961;
const NATIONAL_DAY_BASE_URL: &str = "https://www.nationaldaycalendar.com";

#[tokio::main]
async fn main() {
    let token = env::var("DISCORD_TOKEN").expect("Missing DISCORD_TOKEN environment variable");
    let intents = GatewayIntents::GUILD_MESSAGES;
    let serenity_client = serenity::Client::builder(&token, intents)
        .await
        .expect("Error creating client");
    let db_connection = rusqlite::Connection::open(DB_PATH).expect("Failed to open db");
    let date = OffsetDateTime::now_utc().date();
    let ymd_date = date
        .format(format_description!("[year]-[month]-[day]"))
        .expect("Failed to format ymd date");
    let mut statement = db_connection
        .prepare("SELECT name, url FROM NationalDay WHERE occurrence_2024 = ?1")
        .expect("Failed preparing statement");
    let national_day_iter = statement
        .query_map([&ymd_date], |row| Ok((row.get(0)?, row.get(1)?)))
        .expect("Statement query map failed");
    let mut message = date
        .format(format_description!(
            "[month repr:long] [day padding:none], [year]"
        ))
        .expect("Failed to format display date");
    for day in national_day_iter {
        let (name, url): (String, String) = day.unwrap();
        message.reserve(name.len() + url.len() + NATIONAL_DAY_BASE_URL.len() + 7);
        message.push_str(" | [");
        message.push_str(&name);
        message.push_str("](");
        message.push_str(NATIONAL_DAY_BASE_URL);
        message.push_str(&url);
        message.push(')');
    }
    let birthday: Option<String> = db_connection
        .query_row(
            "SELECT description FROM Birthday WHERE date = ?1",
            [&ymd_date],
            |row| row.get(0),
        )
        .optional()
        .expect("Birthday query failed");
    if let Some(s) = birthday {
        message.reserve(s.len() + 3);
        message.push_str(" | ");
        message.push_str(&s);
    }
    if let Err(err) = ChannelId::new(CHANNEL_ID)
        .say(&serenity_client.http, message)
        .await
    {
        eprintln!("Error saying message: {err:?}");
    }
}
