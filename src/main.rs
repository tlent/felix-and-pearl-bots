use anyhow::{anyhow, Result};
use rusqlite::OptionalExtension;
use serde_json::json;
use std::env;
use time::macros::format_description;
use time::{Date, OffsetDateTime};

const NATIONAL_DAY_BASE_URL: &str = "https://www.nationaldaycalendar.com";
const DISCORD_API_URL: &str = "https://discord.com/api/v10";
const OPENAI_API_URL: &str = "https://api.openai.com/v1/chat/completions";
const MODEL: &str = "gpt-4o";
const DB_PATH: &str = "days.db";
const CHANNEL_ID: u64 = 1218191951237742612;
const DISCORD_MAX_MESSAGE_LEN: usize = 2000;

#[tokio::main]
async fn main() -> Result<()> {
    let openai_api_key = env::var("OPENAI_API_KEY")?;
    let discord_token = env::var("DISCORD_TOKEN")?;
    let db_connection = rusqlite::Connection::open(DB_PATH)?;
    let http_client = reqwest::Client::new();
    let date = OffsetDateTime::now_utc().date();
    let ymd_date = date.format(format_description!("[year]-[month]-[day]"))?;
    let national_days = get_national_days(&db_connection, &ymd_date)?;
    let birthday = get_birthday(&db_connection, &ymd_date)?;
    let llm_message = generate_llm_message(
        &http_client,
        &openai_api_key,
        date,
        &national_days,
        birthday.as_deref(),
    )
    .await?;
    let message = build_message(date, &national_days, birthday.as_deref(), &llm_message)?;
    if message.len() <= DISCORD_MAX_MESSAGE_LEN {
        send_discord_message(&http_client, &discord_token, &message).await?;
    } else {
        send_multipart_discord_message(&http_client, &discord_token, &message).await?;
    }
    Ok(())
}

fn get_national_days(
    db_connection: &rusqlite::Connection,
    ymd_date: &str,
) -> Result<Vec<(String, String)>> {
    let mut statement =
        db_connection.prepare("SELECT name, url FROM NationalDay WHERE occurrence_2025 = ?1")?;
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

async fn generate_llm_message(
    http_client: &reqwest::Client,
    openai_api_key: &str,
    date: Date,
    national_days: &[(String, String)],
    birthday: Option<&str>,
) -> Result<String> {
    let formatted_date = date.format(format_description!(
        "[weekday], [month repr:long] [day padding:none], [year]"
    ))?;
    let formatted_national_days = national_days
        .iter()
        .map(|(name, _)| name.as_str())
        .collect::<Vec<_>>()
        .join("\n");
    let birthday_line = birthday
        .map(|s| format!("Today is also {s}!\n"))
        .unwrap_or_default();
    let prompt = format!(
        "Today's date is {formatted_date}. The following are today's national days:\n\
        {formatted_national_days}\n\
        {birthday_line}\
        You are creating a message in the voice of our family's black and white cat Felix. \
        Generate a playful and funny message relevant to today and these national days. \
        Include relevant and humorous emojis. Don't include any hashtags. \
        You recently renamed yourself Sir Felix Whiskersworth. \
        Use a fancy writing style to match your new name."
    );
    let request_body = json!(
        {
            "model": MODEL,
            "messages": [
                { "role": "user", "content": prompt}
            ]
        }
    )
    .to_string();
    println!("{request_body}");
    let response = http_client
        .post(OPENAI_API_URL)
        .header(reqwest::header::CONTENT_TYPE, "application/json")
        .header(
            reqwest::header::AUTHORIZATION,
            format!("Bearer {openai_api_key}"),
        )
        .body(request_body)
        .send()
        .await?;
    if !response.status().is_success() {
        return Err(anyhow!(response.text().await?));
    }
    let response_body = response.text().await?;
    println!("{response_body}");
    let json: serde_json::Value = serde_json::from_str(&response_body)?;
    let llm_message = json["choices"][0]["message"]["content"]
        .as_str()
        .unwrap()
        .to_owned();
    Ok(llm_message)
}

fn build_message(
    date: Date,
    national_days: &[(String, String)],
    birthday: Option<&str>,
    llm_message: &str,
) -> Result<String> {
    let mut message = date.format(format_description!(
        "[weekday], [month repr:long] [day padding:none], [year]"
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
    message.push('\n');
    message.push_str(llm_message);
    Ok(message)
}

async fn send_multipart_discord_message(
    client: &reqwest::Client,
    discord_token: &str,
    message: &str,
) -> Result<()> {
    let mut current_message = String::new();
    let paragraphs = message.split_inclusive("\n\n");
    for paragraph in paragraphs {
        if current_message.len() + paragraph.len() > DISCORD_MAX_MESSAGE_LEN {
            send_discord_message(client, discord_token, &current_message).await?;
            current_message.clear();
        }
        current_message.push_str(paragraph);
    }
    if !current_message.is_empty() {
        send_discord_message(client, discord_token, &current_message).await?;
    }
    Ok(())
}

async fn send_discord_message(
    client: &reqwest::Client,
    discord_token: &str,
    message: &str,
) -> Result<()> {
    let response = client
        .post(format!("{DISCORD_API_URL}/channels/{CHANNEL_ID}/messages"))
        .header(
            reqwest::header::AUTHORIZATION,
            format!("Bot {discord_token}"),
        )
        .header(reqwest::header::CONTENT_TYPE, "application/json")
        .body(json!({ "content": message }).to_string())
        .send()
        .await?;
    if !response.status().is_success() {
        return Err(anyhow!(response.text().await?));
    }
    Ok(())
}
