use anyhow::Result;
use rusqlite::OptionalExtension;
use std::env;
use time::macros::format_description;
use time::{Date, OffsetDateTime};

const NATIONAL_DAY_BASE_URL: &str = "https://www.nationaldaycalendar.com";
const DISCORD_API_URL: &str = "https://discord.com/api/v10";
const DB_PATH: &str = "days.db";
const CHANNEL_ID: u64 = 1108866354980855961;

#[tokio::main]
async fn main() -> Result<()> {
    let discord_token = env::var("DISCORD_TOKEN")?;
    let db_connection = rusqlite::Connection::open(DB_PATH)?;
    let http_client = reqwest::Client::new();
    let date = OffsetDateTime::now_utc().date();
    let ymd_date = date.format(format_description!("[year]-[month]-[day]"))?;
    let national_days = get_national_days(&db_connection, &ymd_date)?;
    let birthday = get_birthday(&db_connection, &ymd_date)?;
    let message = build_message(date, &national_days, birthday.as_deref())?;
    send_discord_message(&http_client, &discord_token, &message).await?;
    Ok(())
}

fn get_national_days(
    db_connection: &rusqlite::Connection,
    ymd_date: &str,
) -> Result<Vec<(String, String)>> {
    let mut statement =
        db_connection.prepare("SELECT name, url FROM NationalDay WHERE occurrence_2024 = ?1")?;
    let rows = statement.query_map([&ymd_date], |row| Ok((row.get(0)?, row.get(1)?)))?;
    let mut days = vec![];
    for day in rows {
        days.push(day?);
    }
    Ok(days)
}

fn get_birthday(db_connection: &rusqlite::Connection, ymd_date: &str) -> Result<Option<String>> {
    Ok(db_connection
        .query_row(
            "SELECT description FROM Birthday WHERE date = ?1",
            [&ymd_date],
            |row| row.get(0),
        )
        .optional()?)
}

fn build_message(
    date: Date,
    national_days: &[(String, String)],
    birthday: Option<&str>,
) -> Result<String> {
    let mut message = date.format(format_description!(
        "[month repr:long] [day padding:none], [year]"
    ))?;
    for (name, url) in national_days {
        message.reserve(name.len() + url.len() + NATIONAL_DAY_BASE_URL.len() + 7);
        message.push_str(" | [");
        message.push_str(name);
        message.push_str("](");
        message.push_str(NATIONAL_DAY_BASE_URL);
        message.push_str(url);
        message.push(')');
    }
    if let Some(s) = birthday {
        message.reserve(s.len() + 3);
        message.push_str(" | ");
        message.push_str(s);
    }
    Ok(message)
}

async fn send_discord_message(
    client: &reqwest::Client,
    discord_token: &str,
    message: &str,
) -> Result<reqwest::Response> {
    Ok(client
        .post(format!("{DISCORD_API_URL}/channels/{CHANNEL_ID}/messages"))
        .header(
            reqwest::header::AUTHORIZATION,
            format!("Bot {discord_token}"),
        )
        .body(format!("{{ \"content\": \"{message}\" }}"))
        .send()
        .await?)
}
