use reqwest::header::AUTHORIZATION;
use reqwest::{Client, Response, Result};
use rusqlite::OptionalExtension;
use std::env;
use time::macros::format_description;
use time::OffsetDateTime;

const NATIONAL_DAY_BASE_URL: &str = "https://www.nationaldaycalendar.com";
const DISCORD_API_URL: &str = "https://discord.com/api/v10";
const DB_PATH: &str = "days.db";
const CHANNEL_ID: u64 = 1108866354980855961;

#[tokio::main]
async fn main() {
    let discord_token =
        env::var("DISCORD_TOKEN").expect("Missing DISCORD_TOKEN environment variable");
    let db_connection = rusqlite::Connection::open(DB_PATH).expect("Failed to open db");
    let http_client = Client::new();
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
    if let Err(err) = send_discord_message(&http_client, &discord_token, &message).await {
        eprintln!("Error saying message: {err:?}");
    }
}

async fn send_discord_message(
    client: &Client,
    discord_token: &str,
    message: &str,
) -> Result<Response> {
    client
        .post(format!("{DISCORD_API_URL}/channels/{CHANNEL_ID}/messages"))
        .header(AUTHORIZATION, format!("Bot {discord_token}"))
        .body(format!("{{ \"content\": \"{message}\" }}"))
        .send()
        .await
}
