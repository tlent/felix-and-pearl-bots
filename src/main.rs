use anyhow::{anyhow, Result};
use rusqlite::OptionalExtension;
use serde_json::json;
use std::env;
use time::macros::format_description;
use time::{Date, OffsetDateTime};

const NATIONAL_DAY_BASE_URL: &str = "https://www.nationaldaycalendar.com";
const DISCORD_API_URL: &str = "https://discord.com/api/v10";
const DB_PATH: &str = "days.db";
const CHANNEL_ID: u64 = 1218191951237742612;
const DISCORD_MAX_MESSAGE_LEN: usize = 2000;
const ANTHROPIC_API_URL: &str = "https://api.anthropic.com/v1/messages";
const CLAUDE_MODEL: &str = "claude-3-5-haiku-latest";

#[tokio::main]
async fn main() -> Result<()> {
    let anthropic_api_key = env::var("ANTHROPIC_API_KEY")?;
    let discord_token = env::var("DISCORD_TOKEN")?;
    let db_connection = rusqlite::Connection::open(DB_PATH)?;
    let http_client = reqwest::Client::new();
    let date = OffsetDateTime::now_utc().date();
    let ymd_date = date.format(format_description!("[year]-[month]-[day]"))?;
    let national_days = get_national_days(&db_connection, &ymd_date)?;
    let birthday = get_birthday(&db_connection, &ymd_date)?;
    let llm_message = generate_llm_message(
        &http_client,
        &anthropic_api_key,
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
    api_key: &str,
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
        .map(|s| s.to_string())
        .unwrap_or_else(|| "None".to_string());
    
    let prompt = format!(
        "Today's date is {formatted_date}. Below are today's national days and any special occasions to inspire your message:  
**National Days:** {formatted_national_days}  
**Special Occasions:** {birthday_line}  

You are Sir Felix Whiskersworth, our family's distinguished black-and-white feline, once simply Felix, now knighted for your charm and wisdom. Your task is to craft a daily message that transforms today's national days and any special occasions (like birthdays) into a single, captivating tale or reflection, as seen through your sharp, cat-like eyes.  

Here's how to make it purrfect:  
- **Weave a Seamless Story:** Blend all the national days and special occasions into one cohesive narrative or witty commentary. Avoid a mere list—let each element flow naturally into the next, as if you're stalking a thread of yarn through the day.  
- **Feline Perspective:** Reflect on these human holidays and events with a cat's curiosity, humor, or indifference. How might they connect to your world of napping, hunting, or preening? Make it uniquely yours.  
- **Tone:** Strike a balance between elegance (befitting your noble title) and playfulness (true to your whiskered spirit). Be witty, charming, and a tad mischievous, but never stiff or silly.  
- **Structure:** Begin with a feline observation about the day—perhaps the weather, a sunbeam, or a human's antics. Then, deftly tie in the national days and special occasions, letting your thoughts pounce from one to the next. Conclude with a clever, cat-inspired quip or a gracious farewell.  
- **Emojis:** Sprinkle in 3–5 relevant, humorous emojis to amplify your personality (e.g., 🐾 for paw prints, 😸 for feline glee). No hashtags allowed—this isn't a social media chase!  

End your message with a dashing sign-off, such as \"Yours in whiskers and wisdom, Sir Felix Whiskersworth,\" tailored to the day's mood. Keep it concise yet rich—think of it as a purrfectly groomed coat: sleek, shiny, and full of character. Now, unleash your feline brilliance!"
    );
    
    let request_body = json!(
        {
            "model": CLAUDE_MODEL,
            "messages": [
                { "role": "user", "content": prompt }
            ],
            "max_tokens": 1000
        }
    )
    .to_string();
    
    println!("{request_body}");
    let response = http_client
        .post(ANTHROPIC_API_URL)
        .header(reqwest::header::CONTENT_TYPE, "application/json")
        .header("x-api-key", api_key)
        .header("anthropic-version", "2023-06-01")
        .body(request_body)
        .send()
        .await?;
        
    if !response.status().is_success() {
        return Err(anyhow!(response.text().await?));
    }
    
    let response_body = response.text().await?;
    println!("{response_body}");
    let json: serde_json::Value = serde_json::from_str(&response_body)?;
    let llm_message = json["content"][0]["text"]
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
